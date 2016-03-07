# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 13:28:58 2015

@author: Mahlon Barrault (mahlonbarrault@gmail.com)

This file contains code to further clean data from the Zen Map Calgary Metro
Extract OpenStreetMaps data.
"""


# Instructor Code
def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('DBAAdmin:27017')
    db = client[db_name]
    return db


def get_all_docs(db):
    return db.calgary_canada_osm.find({'address.street' : {'$exists' : 1}})


# Instructor Code
def aggregate(db, pipeline):
    result = db.calgary_canada_osm.aggregate(pipeline)
    return result


def update_dirty_docs(db, changes):
    for c in changes.keys():
        db.calgary_canada_osm.update({'address.street' : c}, {'$set' : {'address.street' : changes[c]}})

db = get_db('osm')

changes = {'Rivercrest Drive South-east' : 'Rivercrest Drive SE'}
update_dirty_docs(db, changes)
