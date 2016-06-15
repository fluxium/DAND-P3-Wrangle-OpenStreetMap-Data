"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "calgary_canada.osm"

# 
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


ST_TYPE_EXPECTED = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place",
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons", 'Terrace',
            'Way', 'Rise', 'Point', 'Plaza', 'Park', 'Landing', 'Hollow',
            'Highway', 'Gate', 'Crescent', 'Close', 'Bay', 'Manor', 'Circle']
            
DIR_EXPECTED = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']
            
ST_TYPE_MAPPING = { "St": "Street",
            "St.": "Street",
            'street' : 'Street',
            "Rd." : 'Road',
            'Ave' : "Avenue",
            'Cres' : 'Crescent',
            'Blvd' : 'Boulevard',
            'Blvd.' : 'Boulevard'
            }

# Instructor Code
def audit_street_type(street_types, street_name):
    '''
    Modfies street_types dict. Adds street_name to dict if it does not have
    a conformed street type or conformed directional suffix.
    '''
    m = get_suffix(street_name)
    if m:
        street_type = m.group()
        if street_type not in ST_TYPE_EXPECTED:
                street_types[street_type].add(street_name)

def get_suffix(street_name):
    '''
    Returns the last word from street_name with any directional suffixes
    removed.
    '''
    # DEBUG: REMVOED A SET OF PARENS AROUND INNER STATEMENT
    # sub 
    return street_type_re.search(street_type_re.sub(remove_dir, street_name))


def remove_dir(m):
    '''
    Accepts a RegEx match. Returns and empty string if the match is an
    expected directional suffix. Returns the whole match if it is not a 
    directional suffix.
    '''
    if m.group().upper() in DIR_EXPECTED:
        return ''
    else:
        return m.group()
    return 

# Instructor Code
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# Instructor Code
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types

def find_tags_with_attrib(osmfile, attrib):
    osm_file = open(osmfile, "r")
    tags = defaultdict(int)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if attrib in elem.attrib:
            tags[elem.tag] += 1
    
    return tags

# http://stackoverflow.com/questions/3543559/python-regex-match-and-replace
def process_match(m):
    '''
    Returns the value from ST_TYPE_MAPPING with corresponding key from RegEx
    search. If no key exists the orginal search results from m are returned 
    unmodified.
    '''
    if ST_TYPE_MAPPING.get(m.group()) != None:
        return ST_TYPE_MAPPING.get(m.group())
    else:
        return m.group()
    return 


def update_name(name):
    ''' 
    Returns conformed name if there was a mapping in ST_TYPE_MAPPING.
    Otherwise returns name.
    '''
    return street_type_re.sub(process_match, name)



#st_types = audit(OSMFILE)
#pprint.pprint(dict(st_types))

#for st_type, ways in st_types.iteritems():
#    for name in ways:
#        better_name = update_name(name)
#        print name, "=>", better_name
