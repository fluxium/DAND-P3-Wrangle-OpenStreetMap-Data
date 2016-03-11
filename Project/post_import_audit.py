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


db = get_db('wrangling', '40.78.26.96:27017', 'docdbadmin', '')
#pipeline = make_pipeline()
#result = aggregate(db, pipeline)
result = get_all_docs(db)
street_types = defaultdict(set)

for d in result:
    #print d['address']['street']
    audit_street_type(street_types, d['address']['street'], d['_id'])
    
pprint.pprint(dict(street_types))