# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 13:28:58 2015

@author: Mahlon Barrault (mahlonbarrault@gmail.com)

This file contains code to validate cleaning done to the Zen Map Calgary Metro
Extract OpenStreetMaps data.
"""

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
                    {'street' : '$address.street'}
                }           
                ]
    return pipeline
    
def postal_pipeline():
    pipeline = [
                    {
                        '$project' : {
                                        'postal_code' : '$address.postcode',
                                        'size' : '$address.postcode.length'
                                      }
                    },
                    {'$match' : {'size' : { '$gt' : 5}}}
                ]
    return pipeline

def get_all_docs(db):
    return db.DANDP3.find()

# Instructor Code
def aggregate(db, pipeline):
    result = db.DANDP3.aggregate(pipeline)
    return result

def get_largest_doc(results):
    max_doc_len = 0
    max_doc = {}
    for r in results:
        current_len = len(str(r))
        if current_len > max_doc_len:
            max_doc_len = current_len
            max_doc = r
    return (max_doc_len, max_doc)

db = get_db('wrangling', '40.78.26.96:27017', 'docdbadmin', '')
#pipeline = make_pipeline()
#result = aggregate(db, pipeline)
#print db.calgary_canada_osm.count()
#print get_largest_doc(get_all_docs(db))

docs = db.DANDP3.aggregate(make_pipeline())