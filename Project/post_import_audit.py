# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 13:28:58 2015

@author: Mahlon Barrault (mahlonbarrault@gmail.com)

This file contains code to validate cleaning done to the Zen Map Calgary Metro
Extract OpenStreetMaps data.
"""
import re
import pprint
from collections import defaultdict

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

ST_TYPE_EXPECTED = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place",
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons", 'Terrace',
            'Way', 'Rise', 'Point', 'Plaza', 'Park', 'Landing', 'Hollow',
            'Highway', 'Gate', 'Crescent', 'Close', 'Bay', 'Manor', 'Circle']
            
DIR_EXPECTED = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']
            

# Instructor Code
def get_db(db_name, server_name, username, password):
    from pymongo import MongoClient
    
    client = MongoClient(server_name)
    db = client[db_name]
    db.authenticate(username, password, source='admin')
    
    return db


def make_pipeline():
    pipeline = [
                {'$project': 
                    {'street' : '$address.street'}}           
                ]
    return pipeline

def get_all_docs(db):
    return db.DANDP3.find({'address.street' : {'$exists' : 1}})


# Instructor Code
def audit_street_type(street_types, street_name, docid):
    
    if street_name != None:
        m = get_suffix(street_name)
        if m:
            street_type = m.group()
            if street_type not in ST_TYPE_EXPECTED:
                    street_types[street_type].add((street_name, docid))
    
    #return street_types
    
    
def get_suffix(street_name):
    # IF the first match is a direction abreviation remove it and then search
    # search the string again    
    return street_type_re.search((street_type_re.sub(remove_dir, street_name)))


def remove_dir(m):
    if m.group().upper() in DIR_EXPECTED:
        return ''
    else:
        return m.group() 


db = get_db('wrangling', '40.78.26.96:27017', 'docdbadmin', '***REMOVED***')
#pipeline = make_pipeline()
#result = aggregate(db, pipeline)
result = get_all_docs(db)
street_types = defaultdict(set)

for d in result:
    #print d['address']['street']
    audit_street_type(street_types, d['address']['street'], d['_id'])
    
pprint.pprint(dict(street_types))

# http://stackoverflow.com/questions/29577713/string-field-value-length-in-mongodb
db.DANDP3.find({'address.postcode' : {'$exists': 'true'}, '$where' : "this.address.postcode.length < 7"})
bad_postcode_docs = db.DANDP3.find({'address.postcode' : {'$exists': 'true', '$not' : re.compile('^([A-Z]\d[A-Z]( )\d[A-Z]\d)')}})

postcode_fix = defaultdict(set)
bad_postcode_count = 0

for d in bad_postcode_docs:
    postcode_fix[d['address']['postcode']] = ''
    bad_postcode_count += 1

print 'Bad Postcode Dictionary: ' + str(postcode_fix)
print 'Bad Postcodes' + str(bad_postcode_count)
print 'Unique Bad Postcodes' + str(len(postcode_fix.keys()))

"""
These are the problem postcodes:

{u'T3a4b3': 'T3A 4B3', u'T1X1L8': 'T1X 1L8', u'T3A0H7': 'T3A 0H7', u' T2J 0P8': 'T2J 0P8', u'T3J4L8': 'T3J 4L8', u'T3N0E4': 'T3N 0E4', u't3G 5T3': 'T3G 5T3', u'T3J0S3': 'T3J 0S3', u'T2P3P8': 'T2P 3P8', u'T2E': '', u'T3N0A6': 'T3N 0A6', u't3c2h6': 'T3C 2H6', u'T2G0H7': 'T2G 0H7', u'AB T2S 2N1': 'T2S 2N1', u'T3A5R8': 'T3A 5R8', u'AB T2G 2L2': 'T2G 2L2', u'1212': '', u't2n 3P3': 'T2N 3P3', u'T3R0A1': 'T3R 0A1', u'T3K-5P4': 'T3K 5P4', u'T2P0W3': 'T2P 0W3', u'T2T0A7;T2T 0A7': 'T2T 0A7', u'T2R0E7': 'T2R 0E7', u'T2J2T8': 'T2J 2T8', u'T2L1G1': 'T2L 1G1', u'T3A6J1': 'T3A 6J1', u't2n 4l7': 'T2N 4L7', u'T3G2V7': 'T3G 2V7', u'T3J0G7': 'T3J 0G7', u'T2V2X3': 'T2V 2X3', u'T3B3X3': 'T3B 3X3', u'T3R0H3': 'T3R 0H3', u'403-719-6250': ''}

Fixes were imputted manually
"""