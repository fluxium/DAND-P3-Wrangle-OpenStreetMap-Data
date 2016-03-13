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

db = get_db('wrangling', '40.78.26.96:27017', 'docdbadmin', '***REMOVED***')
all_docs = list(get_all_docs(db))

# Number of Documents, 863038
print 'Number of Documents: ' + str(db.DANDP3.count())

# Largest Document, (112886)
# This is computationally intensive 
#print 'Largest Document: ' + get_largest_doc(all_docs)

docs = aggregate(db, user_pipeline())
users = get_users(docs)

# Number of Unique Users
print 'Number of Unique Users: ' + str(len(users))

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

# Additional Analysis
# How many places accept bitcoin, 18
len(list(db.DANDP3.find({"payment:bitcoin" : "yes"})))

# What are the top amenties?
amenites = list(aggregate(db, [{'$match' : {'amenity' : {'$exists' : 1}}},\
                               {'$group' : {'_id' : '$amenity', 'count' : \
                               {'$sum' : 1}}}, {'$sort' : {'count' : -1}}]))
print amenites[0:3]

# http://api.mongodb.org/python/current/examples/aggregation.html
# Pymongo MapReduce Example
from bson.code import Code
mapper = Code("""
               function () {
                 this.tags.forEach(function(z) {
                   emit(z, 1);
                 });
               }
               """)

reducer = Code("""
                function (key, values) {
                  var total = 0;
                  for (var i = 0; i < values.length; i++) {
                    total += values[i];
                  }
                  return total;
                }
               """)
               
result = db.DANDP3.map_reduce(mapper, reducer, "myresults")
keys = list(result.find())


"""
http://stackoverflow.com/questions/2298870/mongodb-get-names-of-all-keys-in-collection
Executed using linux mongo client to get list of unique keys
mr = db.runCommand({
  "mapreduce" : "DANDP3",
  "map" : function() {
    for (var key in this) { emit(key, null); }
  },
  "reduce" : function(key, stuff) { return null; }, 
  "out": "DANDP3" + "_keys"
})

Results:

[
        "FIXME",
        "FIXME-range",
        "FIXME-rnage",
        "Icn_ref",
        "RBC",
        "_id",
        "abutters",
        "access",
        "address",
        "admin_level",
        "advertising",
        "aerialway",
        "aerialway:bicycle",
        "aeroway",
        "alt_name",
        "alt_name:en",
        "amenity",
        "area",
        "artist_name",
        "artwork_type",
        "atm",
        "attraction",
        "attribution",
        "automated",
        "backrest",
        "barrier",
        "basin",
        "bench",
        "bicycle",
        "bicycle:backward",
        "bicycle_parking",
        "board_type",
        "boat",
        "boundary",
        "brand",
        "bridge",
        "bridge:name",
        "building",
        "building:colour",
        "building:flats",
        "building:levels",
        "building:shape",
        "bus",
        "bus_routes",
        "busway:right",
        "c",
        "cable",
        "cables",
        "capacity",
        "capacity:disabled",
        "capacity:parent",
        "capacity:women",
        "catmp-RoadID",
        "check_date",
        "color",
        "colour",
        "comment",
        "construction",
        "contact:email",
        "contact:fax",
        "contact:phone",
        "contact:website",
        "country",
        "courts",
        "covered",
        "cr:blue:men",
        "cr:blue:woman",
        "cr:green:men",
        "cr:green:woman",
        "cr:white:men",
        "cr:white:woman",
        "craft",
        "created",
        "crossing",
        "crossing:barrier",
        "crossing:bell",
        "crossing:light",
        "crossing_ref",
        "cuisine",
        "currency:CAD",
        "cutting",
        "cycleway",
        "cycleway:right",
        "dam",
        "day_off",
        "day_on",
        "delivery",
        "denomination",
        "description",
        "designation",
        "destination",
        "direction",
        "dispensing",
        "dist:blue",
        "dist:green",
        "dist:red",
        "dist:white",
        "dist:yellow",
        "distance_marker",
        "disused:leisure",
        "dog",
        "drive-thru_atm",
        "drive_through",
        "ele",
        "electrified",
        "elevated",
        "elevator",
        "email",
        "embankment",
        "emergency",
        "end_date",
        "enforcement",
        "entrance",
        "except",
        "exit_to",
        "facebook",
        "fax",
        "fee",
        "fence_type",
        "fenced",
        "finely_mown",
        "fixme",
        "foot",
        "footway",
        "from",
        "fuel:diesel",
        "fuel:octane_91",
        "furniture",
        "garmin_road_class",
        "garmin_type",
        "gauge",
        "generator:source",
        "geobase:acquisitionTechnique",
        "geobase:datasetName",
        "geobase:routeName1:en",
        "geobase:uuid",
        "gns:adm1",
        "gns:cc1",
        "gns:dms_lat",
        "gns:dms_long",
        "gns:dsg",
        "gns:fc",
        "gns:jog",
        "gns:lat",
        "gns:long",
        "gns:mgrs",
        "gns:n:xx:full_name",
        "gns:n:xx:full_name_nd",
        "gns:n:xx:modify_date",
        "gns:n:xx:nt",
        "gns:n:xx:sort_name",
        "gns:rc",
        "gns:ufi",
        "gns:uni",
        "golf",
        "golf_cart",
        "goods",
        "grade",
        "guage",
        "guidepost",
        "handicap",
        "handrail",
        "health_facility:type",
        "health_facility_type",
        "health_service:test",
        "healthcare",
        "height",
        "heritage",
        "hgv",
        "highway",
        "historic",
        "history",
        "horse",
        "hour_off",
        "hour_on",
        "iata",
        "icao",
        "id",
        "incline",
        "indoor",
        "information",
        "int_name",
        "internet_access",
        "is_in",
        "is_in:city",
        "is_in:continent",
        "is_in:country",
        "is_in:country_code",
        "junction",
        "kerb",
        "key",
        "landcover",
        "landuse",
        "lanes",
        "layer",
        "lcn",
        "lcn_ref",
        "leaf_cycle",
        "leaf_type",
        "leisure",
        "length",
        "level",
        "light_rail",
        "lit",
        "loc_name",
        "local_ref",
        "location",
        "man_made",
        "material",
        "maxheight",
        "maxlength",
        "maxspeed",
        "maxspeed:advisory",
        "medicinal_system:western",
        "members",
        "military",
        "motor_vehicle",
        "motorcar",
        "motorcycle",
        "motorhome",
        "mown",
        "mtb:description",
        "mtb:scale",
        "mtb:scale:imba",
        "mtb:scale:uphill",
        "name",
        "name:ar",
        "name:de",
        "name:en",
        "name:es",
        "name:fr",
        "name:it",
        "name:ru",
        "name:uk",
        "name_1",
        "naptan:Bearing",
        "nat_name:en",
        "nat_name:fr",
        "natural",
        "network",
        "node_refs",
        "node_type",
        "noexit",
        "note",
        "notes",
        "office",
        "old_name",
        "old_ref",
        "oneway",
        "oneway:bicycle",
        "opening_hours",
        "opening_hours:url",
        "operator",
        "outdoor_seating",
        "overflow",
        "par",
        "park_ride",
        "parking",
        "paved",
        "payment:bitcoin",
        "payment:cash",
        "payment:coins",
        "payment:credit_cards",
        "payment:debit_cards",
        "payment:litecoin",
        "phone",
        "piste:difficulty",
        "piste:grooming",
        "piste:type",
        "place",
        "plant",
        "platform",
        "platforms",
        "pme",
        "population",
        "pos",
        "postal_code",
        "power",
        "private",
        "proposed",
        "psv",
        "public_transport",
        "public_transport:version",
        "railway",
        "railway:subdivision",
        "railway_1",
        "ramp",
        "ramp:wheelchair",
        "recycling:batteries",
        "recycling:cans",
        "recycling:cardboard",
        "recycling:cartons",
        "recycling:clothes",
        "recycling:electrical_appliances",
        "recycling:glass",
        "recycling:glass_bottles",
        "recycling:green_waste",
        "recycling:magazines",
        "recycling:newspaper",
        "recycling:paper",
        "recycling:paper_packaging",
        "recycling:plastic",
        "recycling:plastic_bottles",
        "recycling:plastic_packaging",
        "recycling:scrap_metal",
        "recycling:small_appliances",
        "recycling:waste",
        "recycling:wood",
        "recycling_type",
        "ref",
        "reference",
        "reg_name",
        "relation",
        "religion",
        "residential",
        "resource",
        "restriction",
        "ride:type",
        "room",
        "route",
        "route_master",
        "route_ref",
        "routes",
        "seasonal",
        "segregated",
        "self_service",
        "service",
        "service:area",
        "service:location",
        "service_times",
        "shelter",
        "shelter_type",
        "shop",
        "short_name",
        "sidewalk",
        "sign",
        "smoking",
        "social_facility",
        "social_facility:for",
        "source",
        "source:geometry",
        "source:name",
        "source:population",
        "spaces:disabled",
        "speciality",
        "species",
        "speed",
        "sport",
        "sr:blue:men",
        "sr:blue:woman",
        "sr:green:men",
        "sr:green:woman",
        "sr:white:men",
        "sr:white:woman",
        "stars",
        "start_date",
        "state",
        "stop",
        "stop_id",
        "store",
        "store_name",
        "street_lamp",
        "substation",
        "supervised",
        "surface",
        "surveillance",
        "tactile_paving",
        "takeaway",
        "taxi",
        "tee",
        "temporary:access",
        "temporary:bicycle",
        "to",
        "toilets:disposal",
        "toll",
        "tourism",
        "tower:type",
        "tracktype",
        "traffic_calming",
        "traffic_sign",
        "traffic_signals",
        "traffic_signals:direction",
        "trail_visibility",
        "trailer",
        "tunnel",
        "turn:lanes",
        "type",
        "unisex",
        "unit",
        "url",
        "usage",
        "validate:no_name",
        "vehicle:backward",
        "vending",
        "voltage",
        "waste",
        "waste_disposal",
        "water",
        "waterway",
        "website",
        "wetland",
        "wheelchair",
        "wheelchair:description",
        "width",
        "wifi",
        "wikipedia",
        "wood",
        "zoo"
]



"""






