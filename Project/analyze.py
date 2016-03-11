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

def user_pipeline():
    pipeline = [ 
                    {
                        '$group' : {
                                        '_id' : '$created.user', 
                                        'count' : { '$sum' : 1}
                                   }
                    },
                    {
                        '$sort' : { 'count' : -1 }                    
                    }
                ]
    return pipeline

def get_users(cursor):
    users = []
    for d in docs:
        users.append(d)
    return users

# This function was replaced with '$sort' : { 'count' : -1 } in pipeline
def sort_users(users, key):
    from operator import itemgetter
    sorted_users = sorted(users, key=itemgetter(key), reverse = True)
    return sorted_users
    
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
all_docs = get_all_docs(db)

# Number of Documents, 863038
print 'Number of Documents: ' + str(db.DANDP3.count())

# Largest Document, (112886)
# This is computationally intensive 
#print 'Largest Document: ' + get_largest_doc(all_docs)

docs = aggregate(db, user_pipeline())
users = get_users(docs)

# Number of Unique Users
print 'Number of Unique Users: ' + len(users)

# Top Three Contributors
print 'Top Three Contributors: ' + str(users[0:3])

# Rank of My Contributions
mb_rank = 1
for u in users:
    if u['_id'] == 'MahlonBarrault':
        break
    mb_rank += 1
print 'My Rank: ' + str(mb_rank)

# Number of Ways
print 'Number of Ways: ' + str(db.DANDP3.find({"node_type":"way"}).count())

# Number of Nodes
print 'Number of Nodes: ' + str(db.DANDP3.find({"node_type":"node"}).count())
