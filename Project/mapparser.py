#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the 
tag name as the key and number of times this tag can be encountered in 
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

def count_tags(filename):
    # YOUR CODE HERE
    results_tag = defaultdict(int)
    results_a = defaultdict(int)
    with open(filename, 'r') as f:
        for evt, t in ET.iterparse(f):
            results_tag[t.tag] += 1
            for a in t.attrib:
                results_a[a] += 1
            
    return results_tag, results_a

tags, attributes = count_tags('calgary_canada.osm')
print 'Tags:'
pprint.pprint(tags)
print '\nAttributes:'
pprint.pprint(attributes)
    
'''
if __name__ == "__main__":
    test()
'''