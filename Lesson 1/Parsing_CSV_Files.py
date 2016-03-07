# Your task is to read the input DATAFILE line by line, and for the first 10 lines (not including the header)
# split each line on "," and then for each line, create a dictionary
# where the key is the header title of the field, and the value is the value of that field in the row.
# The function parse_file should return a list of dictionaries,
# each data line in the file being a single list entry.
# Field names and values should not contain extra whitespace, like spaces or newline characters.
# You can use the Python string method strip() to remove the extra whitespace.
# You have to parse only the first 10 data lines in this exercise,
# so the returned list should have 10 entries!
import os

DATADIR = ""
DATAFILE = "beatles-diskography.csv"

def parse_file_instructor(datafile): # Instructor Code
    data = []
    with open(datafile, "r") as f:
        header = f.readline().split(",")
        counter = 0
        for line in f:
            if counter == 10:
                break
            
            fields = line.split(",")
            entry = {}
            
            for i, value in enumerate(fields):
                entry[header[i].strip()] = value.strip()
                
            data.append(entry)
            counter += 1
            

def parse_file(datafile):
    data = []
    header = []
    line_num = 0
    with open(datafile, "r") as f:
        for line in f:
            #print line
            line_num += 1
            if line_num == 1:
                header = line.strip().split(',')
            elif line_num <= 11:
                line_temp = line.strip().split(',')
                data.append({header[0]:line_temp[0], header[1]:line_temp[1], header[2]:line_temp[2], header[3]:line_temp[3], header[4]:line_temp[4], header[5]:line_temp[5], header[6]:line_temp[6]})

    return data


def test():
    # a simple test of your implemetation
    datafile = os.path.join(DATADIR, DATAFILE)
    d = parse_file(datafile)
    firstline = {'Title': 'Please Please Me', 'UK Chart Position': '1', 'Label': 'Parlophone(UK)', 'Released': '22 March 1963', 'US Chart Position': '-', 'RIAA Certification': 'Platinum', 'BPI Certification': 'Gold'}
    tenthline = {'Title': '', 'UK Chart Position': '1', 'Label': 'Parlophone(UK)', 'Released': '10 July 1964', 'US Chart Position': '-', 'RIAA Certification': '', 'BPI Certification': 'Gold'}
    #print d
    assert d[0] == firstline
    assert d[9] == tenthline

    
test()