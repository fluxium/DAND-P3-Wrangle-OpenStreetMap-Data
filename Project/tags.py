#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
"""
Your task is to explore the data a bit more.
Before you process the data and add it into MongoDB, you should
check the "k" value for each "<tag>" and see if they can be valid keys in MongoDB,
as well as see if there are any other potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data model
and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with problematic characters.
Please complete the function 'key_type'.
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, regex_keys, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        if lower_colon.search(element.attrib['k']):
            regex_keys['lower_colon'] += 1
        elif problemchars.search(element.attrib['k']):
            regex_keys['problemchars'] += 1
        elif lower.search(element.attrib['k']):
            regex_keys['lower'] += 1
        else:
            regex_keys['other'] += 1
    keys[element.attrib.get('k')].add(element.attrib.get('v'))
    return regex_keys, keys



def process_map(filename):
    regex_keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    keys = defaultdict(set)
    
    for _, element in ET.iterparse(filename):
        regex_keys, keys = key_type(element, regex_keys, keys)
    return regex_keys, keys


regex_keys, keys = process_map('calgary_canada.osm')
print 'RegEx Keys:'
pprint.pprint(regex_keys)
#print '\nAll Keys and Values:'
#pprint.pprint(keys)
kvs = keys.keys()
kvs.sort()
print '\nSorted Keys:'
pprint.pprint(kvs)

'''
if __name__ == "__main__":
    test()
'''