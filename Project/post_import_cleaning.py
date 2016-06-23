# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 13:28:58 2015

@author: Mahlon Barrault (mahlonbarrault@gmail.com)

This file contains code to further clean data from the Zen Map Calgary Metro
Extract OpenStreetMaps data.
"""
import re
from collections import defaultdict

def get_password():
    password_file = open('passwords.txt', 'r')
    return password_file.readline()

# Instructor Code
def get_db(db_name, server_name, username, password):
    from pymongo import MongoClient
    
    client = MongoClient(server_name)
    db = client[db_name]
    db.authenticate(username, password, source='admin')
    
    return db


def get_all_docs(db):
    return db.DANDP3.find({'address.street' : {'$exists' : 1}})


# Instructor Code
def aggregate(db, pipeline):
    result = db.DANDP3.aggregate(pipeline)
    return result


def update_dirty_docs(db, changes):
    for c in changes.keys():
        db.DANDP3.update_one({'address.street' : c}, {'$set' : {'address.street' : changes[c]}})
        
def update_dirty_postcodes(db, changes):
    for c in changes.keys():
        db.DANDP3.update_many({'address.postcode' : c}, {'$set' : {'address.postcode' : changes[c]}})

db = get_db('wrangling', '40.78.26.96:27017', 'docdbadmin', get_password())

street_changes = {'Rivercrest Drive South-east' : 'Rivercrest Drive SE'}
update_dirty_docs(db, street_changes)

#postcode_changes = {u'T3a4b3': 'T3A 4B3', u'T1X1L8': 'T1X 1L8', \
#                    u'T3A0H7': 'T3A 0H7', u' T2J 0P8': 'T2J 0P8', \
#                    u'T3J4L8': 'T3J 4L8', u'T3N0E4': 'T3N 0E4', \
#                    u't3G 5T3': 'T3G 5T3', u'T3J0S3': 'T3J 0S3', \
#                    u'T2P3P8': 'T2P 3P8', u'T2E': '', u'T3N0A6': 'T3N 0A6', \
#                    u't3c2h6': 'T3C 2H6', u'T2G0H7': 'T2G 0H7', \
#                    u'AB T2S 2N1': 'T2S 2N1', u'T3A5R8': 'T3A 5R8', \
#                    u'AB T2G 2L2': 'T2G 2L2', u'1212': '', \
#                    u't2n 3P3': 'T2N 3P3', u'T3R0A1': 'T3R 0A1', \
#                    u'T3K-5P4': 'T3K 5P4', u'T2P0W3': 'T2P 0W3', \
#                    u'T2T0A7;T2T 0A7': 'T2T 0A7', u'T2R0E7': 'T2R 0E7', \
#                    u'T2J2T8': 'T2J 2T8', u'T2L1G1': 'T2L 1G1', \
#                    u'T3A6J1': 'T3A 6J1', u't2n 4l7': 'T2N 4L7', \
#                    u'T3G2V7': 'T3G 2V7', u'T3J0G7': 'T3J 0G7', \
#                    u'T2V2X3': 'T2V 2X3', u'T3B3X3': 'T3B 3X3', \
#                    u'T3R0H3': 'T3R 0H3', u'403-719-6250': ''}
#
#update_dirty_postcodes(db, postcode_changes)

"""
These are the problem postcodes from post_import_audit.py:

{u'T3a4b3': 'T3A 4B3', u'T1X1L8': 'T1X 1L8', u'T3A0H7': 'T3A 0H7', u' T2J 0P8': 'T2J 0P8', u'T3J4L8': 'T3J 4L8', u'T3N0E4': 'T3N 0E4', u't3G 5T3': 'T3G 5T3', u'T3J0S3': 'T3J 0S3', u'T2P3P8': 'T2P 3P8', u'T2E': '', u'T3N0A6': 'T3N 0A6', u't3c2h6': 'T3C 2H6', u'T2G0H7': 'T2G 0H7', u'AB T2S 2N1': 'T2S 2N1', u'T3A5R8': 'T3A 5R8', u'AB T2G 2L2': 'T2G 2L2', u'1212': '', u't2n 3P3': 'T2N 3P3', u'T3R0A1': 'T3R 0A1', u'T3K-5P4': 'T3K 5P4', u'T2P0W3': 'T2P 0W3', u'T2T0A7;T2T 0A7': 'T2T 0A7', u'T2R0E7': 'T2R 0E7', u'T2J2T8': 'T2J 2T8', u'T2L1G1': 'T2L 1G1', u'T3A6J1': 'T3A 6J1', u't2n 4l7': 'T2N 4L7', u'T3G2V7': 'T3G 2V7', u'T3J0G7': 'T3J 0G7', u'T2V2X3': 'T2V 2X3', u'T3B3X3': 'T3B 3X3', u'T3R0H3': 'T3R 0H3', u'403-719-6250': ''}

Fixes were imputted manually
"""

'''
Following is code to programatically clean the postcodes above that were cleaned
by mapping and manually correcting the values previously
'''
# Finds strings that have the correct letter number alternation but might not
# have the correct segment separator
re_valid_post_code = re.compile('[A-Za-z]\d[A-Za-z]( ?\-?)\d[A-Za-z]\d')

post_code_changes = defaultdict(set)
bad_post_codes = []

# following commented block will retreive nonconformed post codes from mongodb
#bad_postcode_docs = db.DANDP3.find({'address.postcode' : {'$exists': 'true', \
#'$not' : re.compile('^([A-Z]\d[A-Z]( )\d[A-Z]\d)')}})
#
#for d in bad_postcode_docs:
#    bad_post_codes.append(d)
    
bad_post_codes = [u'1212', u'T3A6J1', u'T3a4b3', u'T3K-5P4', u'T3R0A1',
                  u'T1X1L8', u't2n 3P3', u'T3A0H7', u' T2J 0P8', u'T2J2T8', 
                  u'T2P0W3', u'T3J4L8', u'T2R0E7', u'T3N0E4', u'T2L1G1',
                  u't3G 5T3', u'T3J0S3', u'T2T0A7;T2T 0A7', u't2n 4l7',
                  u'T3G2V7', u'T3J0G7', u'T2P3P8', u'T2E', u'T3N0A6',
                  u'403-719-6250', u't3c2h6', u'T2V2X3', u'T3B3X3', u'T2G0H7',
                  u'AB T2S 2N1', u'T3R0H3', u'T3A5R8', u'AB T2G 2L2']

for bpc in bad_post_codes:
    match = re_valid_post_code.search(bpc)
    
    if match:
        post_code = match.group()
        post_code = post_code.upper()
        
        if post_code[3] != ' ':
            if len(post_code) <= 6:
                # Insert a space if it is missing
                post_code = post_code[0:3] + ' ' + post_code[3:6]
            elif len(post_code) > 6:
                # post code len is good but char 3 is not a space, replace it
                post_code = post_code.replace(post_code[3], ' ')
        post_code_changes[bpc] = post_code
    else:
        post_code_changes[bpc] = ''
        
update_dirty_postcodes(db, post_code_changes)
        
        
        
        
        
        
        
        