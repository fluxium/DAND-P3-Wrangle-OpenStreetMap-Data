# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 13:28:58 2015

@author: Mahlon Barrault (mahlonbarrault@gmail.com)

This file contains code to validate cleaning done to the Zen Map Calgary Metro
Extract OpenStreetMaps data.
"""


# Instructor Code
def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('DBAAdmin:27017')
    db = client[db_name]
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
                    {'$match' : {'size' : { '$lt' : 7}}}
                ]
    return pipeline

def get_all_docs(db):
    return db.calgary_canada_osm.find()

# Instructor Code
def aggregate(db, pipeline):
    result = db.calgary_canada_osm.aggregate(pipeline)
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

db = get_db('osm')
#pipeline = make_pipeline()
#result = aggregate(db, pipeline)
#print db.calgary_canada_osm.count()
#print get_largest_doc(get_all_docs(db))
docs = aggregate(db, postal_pipeline())