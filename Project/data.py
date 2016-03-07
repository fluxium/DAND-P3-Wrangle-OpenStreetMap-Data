#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function
 with the element
as an argument. You should return a dictionary, containing the shaped data for 
that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value 
pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array 
      are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be 
ignored
- if second level tag "k" value starts with "addr:", it should be added to a 
dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":",
 you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

ST_TYPE_EXPECTED = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place",
                    "Square", "Lane", "Road", "Trail", "Parkway", "Commons"]

ST_TYPE_MAPPING = { "St": "Street",
            "St.": "Street",
            "Rd." : 'Road',
            'Ave' : "Avenue"
            }


def shape_base(element):
    
    node = defaultdict()    
    
    created_keys = ["version", "changeset", "timestamp", "user", "uid"]
    root_keys = ['id', 'visible']    
    
    node['type'] = element.tag
    node['created'] = defaultdict()
    
    # Probably could use the .get() method on element here
    if 'lat' in element.attrib and 'lon' in element.attrib:
        node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]       

    # http://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops-in-python    
    for k, v in (element.attrib).iteritems():
        if k in created_keys:
            node['created'][k] = v
        elif k in root_keys:
            node[k] = v
            
    return shape_node(node, element)
    

def regex_key(k):
    l = lower.search(k)
    lc = lower_colon.search(k)
    pc = problemchars.search(k)

    return l, lc, pc


def shape_node(node, element):
    
    node_refs = []
    address = defaultdict()    
    
    for t in element:
        k = t.attrib.get('k')
        v = t.attrib.get('v')
        r = t.attrib.get('ref')
        
        if k:
            l, lc, pc = regex_key(k)       
            if pc == None:
                if k.startswith('addr'):
                    if lc:
                        # FIXME The v in this line need to be run through data 
                        # cleaning for street types
                        address[k.split(':')[1]] = v
                    else:
                        continue
                else:
                    node[k] = v
        if r:
            node_refs.append(r)
            
        if len(address) > 0:
            node['address'] = address
        if len(node_refs) > 0:
            node['node_refs'] = node_refs
    return node


def shape_element(element):
    node = {}
    
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node = shape_base(element)
        
        return dict(node)
    else:
        return None

# Instructor code from audit.py
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in ST_TYPE_EXPECTED:
            street_types[street_type].add(street_name)

# Instructor code from audit.py
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# Instructor code from audit.py
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


# http://stackoverflow.com/questions/3543559/python-regex-match-and-replace
def process_match(m):
    if ST_TYPE_MAPPING.get(m.group()) != None:
        return ST_TYPE_MAPPING.get(m.group())
    else:
        return m.group()
    return 


def update_name(name): 
    return street_type_re.sub(process_match, name)


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('example.osm', True)
    #pprint.pprint(data)
    #print data

    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()