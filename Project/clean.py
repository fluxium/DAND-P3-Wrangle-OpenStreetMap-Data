# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 16:18:44 2015

@author: Mahlon Barrault (mahlonbarrault@gmail.com)

This file contains the code to clean the Map Zen Calgary Metro Area
OpenStreetMaps data extract. This code will output a cleaned JSON file that can
be imported in to MongoDB for further analysis

Some code was provided by the authors and instructors of 
Udacity - Data Wrangling with MongoDB
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs
import json

OSMFILE = "calgary_canada.osm"

# RegEx for various key validations. All provided by Instructor Code
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

lower = re.compile(r'^([a-z]|_)*$')

# Useful for fiding k values like addr:street
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')

# Useful for discovering values with characters that would be problematic for
# keys in MongoDB
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# These values were collected form audit.py. They represent the street types
# present in the data that do not need to be conformed
ST_TYPE_EXPECTED = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place",
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons", 'Terrace',
            'Way', 'Rise', 'Point', 'Plaza', 'Park', 'Landing', 'Hollow',
            'Highway', 'Gate', 'Crescent', 'Close', 'Bay', 'Manor', 'Circle']


# These values were collectect from audit.py. They are the values that were not
# present in the list of acceptable street types.
ST_TYPE_MAPPING = { "St": "Street",
                   "St.": "Street",
                   'street' : 'Street',
                   "Rd." : 'Road',
                   "Rd" : 'Road',
                   'Ave' : "Avenue",
                   'Ave.' : "Avenue",
                   'Cres' : 'Crescent',
                   'Cres.' : 'Crescent',
                   'Blvd' : 'Boulevard',
                   'Blvd.' : 'Boulevard'
                   }


# These values are the conformed format for street directions
DIR_EXPECTED = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']

        
# These values were collected from audit.py. They represent all of the
# inconsistancies in the direction suffixes and the corresponding mapping to
# the conformed values
DIR_MAPPING = {'East' : 'E',
               'N.E.' : 'NE',
               'N.E' : 'NE',
               'N.W' : 'NW',
               'N.W.' : 'NW',
               'North' : 'N',
               'Northeast' : 'NE',
               'Northwest' : 'NW',
               'S.E' : 'SE',
               'S.E.' : 'SE',
               'S.W' : 'SW',
               'S.W.' : 'SW',
               'South' : 'S',
               'South-west' : 'SW',
               'Southeast' : 'SE',
               'South-east' : 'SE',
               'Southwest' : 'SW',
               'West' : 'W'
               }

# Instructor Code
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


def shape_element(element):
    ''' Returns a node with the basic initial structure'''
    node = {}
    if element.tag == 'node' or element.tag == 'way' \
        or element.tag == 'relation':
        node = shape_base(element)
    return node
    

def shape_base(element):
    ''' Creates top level structure for element then calls shape_node to build
    Node details.
    '''
    node = defaultdict()    
    
    # Keys for the created dictionary
    created_keys = ["version", "changeset", "timestamp", "user", "uid"]
    root_keys = ['id', 'visible']    
    
    node['node_type'] = element.tag
    node['created'] = defaultdict()
    
    # Probably could use the .get() method on element here
    if 'lat' in element.attrib and 'lon' in element.attrib:
        node['pos'] = [float(element.attrib['lat']), \
            float(element.attrib['lon'])]       

    # http://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops-in-python    
    for k, v in (element.attrib).iteritems():
        if k in created_keys:
            node['created'][k] = v
        elif k in root_keys:
            node[k] = v
            
    return shape_node(node, element)
 
# This function does several things. It should be broken in to separate concerns
def shape_node(node, element):
    ''' Builds structure for node details. Extracts tags and transforms them to
    key-value pairs on the node.
    '''
    node_refs = []
    address = defaultdict()    
    members = []
    member_keys = ["type", "ref", "role"]        
    
    for t in element:
        if t.tag == 'tag':
            k = t.attrib.get('k')
            v = t.attrib.get('v')
            
            # Ensure the key is not multi-part or containing invalid chars for 
            # keys in mongodb
            l, lc, pc = regex_key(k)
            
            # Keys with illegal characters for mondodb keys are not added
            if pc == None:
                if k.startswith('addr'):
                    if lc:       
                        address[k.split(':')[1]] = update_st_name(v)
                    else:
                        continue
                elif k == 'created_by':
                    node['created'][k] = v
                else:
                    node[k] = v
        elif t.tag == 'nd':
            r = t.attrib.get('ref')
            node_refs.append(r)
        elif t.tag == 'member':
            member = defaultdict()
            for a in member_keys:
                member[a] = t.attrib.get(a)
            members.append(member)
        
            
    if len(address) > 0:
        node['address'] = address
    if len(node_refs) > 0:
        node['node_refs'] = node_refs
    if len(members) > 0:
        node['members'] = members
    return node
   

def regex_key(k):
    ''' Check for nonconformed or invalid characters'''
    l = lower.search(k)
    lc = lower_colon.search(k)
    pc = problemchars.search(k)

    return l, lc, pc


def update_st_name(street_name):
    ''' Recursive function to conform street types and directional suffixes'''
    street_name = street_name.split(',')[0]

    init_search = street_type_re.search(street_name)
    
    if init_search:
        init_search = init_search.group()
        
        if init_search in DIR_EXPECTED:
            # street_name should now have the street type exposed on the end
            # of the string
            street_name = street_type_re.sub(remove_suffix, street_name)
            # Recusive call to have the funtion check street type. strip() is
            # needed so that the RegEx matches properly
            return str(update_st_name(street_name.strip())) + ' ' + init_search
        elif init_search in DIR_MAPPING:
            dir_clean = DIR_MAPPING[init_search]
            street_name = street_type_re.sub(remove_suffix, street_name)
            # Recusive call to have the funtion check street type. strip() is
            # needed so that the RegEx matches properly
            return str(update_st_name(street_name.strip())) + ' ' + dir_clean
        elif init_search in ST_TYPE_EXPECTED:
            # Recursive base case
            return street_name
        elif init_search in ST_TYPE_MAPPING:
            st_ty_clean = ST_TYPE_MAPPING[init_search]
            street_name = street_type_re.sub(st_ty_clean, street_name)
            # Alternate recursive base case
            return street_name
        else:
            # Catches streets that will not be cleaned like 
            # 'Township Road  204A'
            return street_name
    else:
        # Recursion should not hit this else, something has gone wrong; will
        # return 'None'
        return street_name

# Could be replaced with lambda where this is used
def remove_suffix(m):
    return ''
 
 
