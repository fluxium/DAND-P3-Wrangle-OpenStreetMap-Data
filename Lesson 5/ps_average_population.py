#!/usr/bin/env python
"""
Use an aggregation query to answer the following question. 

Extrapolating from an earlier exercise in this lesson, find the average regional city population 
for all countries in the cities collection. What we are asking here is that you first calculate the 
average city population for each region in a country and then calculate the average of all the 
regional averages for a country. As a hint, _id fields in group stages need not be single values. 
They can also be compound keys (documents composed of multiple fields). You will use the same 
aggregation operator in more than one stage in writing this aggregation query. I encourage you to 
write it one stage at a time and test after writing each stage.

Please modify only the 'make_pipeline' function so that it creates and returns an aggregation 
pipeline that can be passed to the MongoDB aggregate function. As in our examples in this lesson, 
the aggregation pipeline should be a list of one or more dictionary objects. 
Please review the lesson examples if you are unsure of the syntax.

Your code will be run against a MongoDB instance that we have provided. If you want to run this code 
locally on your machine, you have to install MongoDB, download and insert the dataset.
For instructions related to MongoDB setup and datasets please see Course Materials.

Please note that the dataset you are using here is a different version of the cities collection
provided in the course materials. If you attempt some of the same queries that we look at in the 
problem set, your results may be different.
"""

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

'''
                    {'$match' : {'name' : {'$exists' : 1}, 'country' : {'$exists' : 1}, 'isPartOf' : {'$exists' : 1}}},
                    {'$unwind' : '$isPartOf'},
                    {'$group' : 
                        {
                        '_id' : '$isPartOf',
                        'average_population' : {'$avg' : '$population'}
                        }
                    },
                    {'$group' : 
                        {
                        '_id' : '$country',
                        'avgRegionalPopulation' : {'$avg': '$average_population'}
                        }
                    }
'''
'''
project = {$project : {
        "s" : {
            "$ifNull" : [
                "$solved",
                [
                    {
                        "points" : 0
                    }
                ]
            ]
        },
        "login" : 1
    }
};
unwind={$unwind:"$s"};
group= { "$group" : {
        "_id" : "$_id",
        "login" : {
            "$first" : "$login"
        },
        "score" : {
            "$sum" : "$s.points"
        }
    }
}
'''
'''
's': { $cond: [{$eq: [{$size: '$solved'}, 0] }, [ { point: 0 } ], '$solved'] }
'''


'''
{
                    '$match' : 
                        {
                        'name' : {'$exists' : 1},
                        'country' : {'$exists' : 1},
                        #'isPartOf' : {'$exists' : 1}
                        }
                    },
                    
                    {'$match' : {'country' : 'Lithuania'}},
'''

def make_pipeline():
    # complete the aggregation pipeline
    pipeline =  [
                    
                    {'$project' : 
                        {
                        'country' : 1,
                        'isPartOf' : {'$ifNull' : ['$isPartOf', ['$country']]},
                        'population' : 1
                        }
                    },
                    {'$unwind' : '$isPartOf'},
                    #{ '$ifNull' : {'isPartOf' : '$isPartOf', 'isPartOf' : '$name'}},
                    {
                    '$group' : 
                        {
                        '_id' : {'country' : '$country', 'region' : '$isPartOf'},
                        'c_r_ave' : {'$avg' : '$population'}
                        }
                    },
                    {
                    '$group' : 
                        {
                        '_id' : '$_id.country',
                        'avgRegionalPopulation' : {'$avg' : '$c_r_ave'}
                        }
                    }
                ]
                
    return pipeline

def aggregate(db, pipeline):
    result = db.cities.aggregate(pipeline)
    return result

if __name__ == '__main__':
    # The following statements will be used to test your code by the grader.
    # Any modifications to the code past this point will not be reflected by
    # the Test Run.
    db = get_db('examples')
    pipeline = make_pipeline()
    result = aggregate(db, pipeline)
    import pprint
    if len(result["result"]) < 150:
        pprint.pprint(result["result"])
    else:
        pprint.pprint(result["result"][:100])
    key_pop = 0
    for country in result["result"]:
        if country["_id"] == 'Lithuania':
            assert country["_id"] == 'Lithuania'
            assert abs(country["avgRegionalPopulation"] - 14750.784447977203) < 1e-10
            key_pop = country["avgRegionalPopulation"]
    assert {'_id': 'Lithuania', 'avgRegionalPopulation': key_pop} in result["result"]
