#!/usr/bin/env python
# -*- coding: utf-8 -*-
# So, the problem is that the gigantic file is actually not a valid XML, because
# it has several root elements, and XML declarations.
# It is, a matter of fact, a collection of a lot of concatenated XML documents.
# So, one solution would be to split the file into separate documents,
# so that you can process the resulting files as valid XML documents.

import xml.etree.ElementTree as ET
PATENTS = 'patent.data'

def get_root(fname):
    tree = ET.parse(fname)
    return tree.getroot()


def split_file(filename):
    # we want you to split the input file into separate files
    # each containing a single patent.
    # As a hint - each patent declaration starts with the same line that was causing the error
    # The new files should be saved with filename in the following format:
    # "{}-{}".format(filename, n) where n is a counter, starting from 0.

# open file
# for each enumerated line
#   if line starts with <?xml record line num
#
#for line numbers starting with <?xml
#   write file[line] to file[line[i + 1] - 1]
    xml_start = []
    lines = []

    with open(filename, "r") as f:
        for i, line in enumerate(f):
            lines.append(line)
            if line.startswith('<?xml'):
                xml_start.append(i)
                
        for i, start in enumerate(xml_start[:-1]):
            f_out = open("{}-{}".format(filename, i), 'w')
            f_out.writelines(lines[start:(xml_start[i + 1] - 1)])
        else: # http://stackoverflow.com/questions/2429098/how-to-treat-the-last-element-in-list-differently-in-python, second answer
            f_out = open("{}-{}".format(filename, i + 1), 'w')            
            f_out.writelines(lines[xml_start[-1]:-1])


def test():
    split_file(PATENTS)
    for n in range(4):
        try:
            fname = "{}-{}".format(PATENTS, n)
            f = open(fname, "r")
            if not f.readline().startswith("<?xml"):
                print "You have not split the file {} in the correct boundary!".format(fname)
            f.close()
        except:
            print "Could not find file {}. Check if the filename is correct!".format(fname)


test()