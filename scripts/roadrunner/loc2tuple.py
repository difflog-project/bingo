#!/usr/bin/env python3

# Args: <output of extract.py> racePairs_cs.txt <output_file>
# Note: all args must be with full paths
# example:
# <path-to>/loc2tuple.py hedc_races.txt racePairs_cs.txt out [dbg]


import logging
import re
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

dynRacesFileName = sys.argv[1]
racePairsFileName = sys.argv[2]
outFileName = sys.argv[3]
if len(sys.argv) == 5:
    debugFlag = sys.argv[4]
else:
    debugFlag = "" 

########################################################################################################################
# 1. Accept Input 

# Format in dynRacesFileName: race Write Spider.java:232 Write weblech/spider/Spider.java:92
dynRaces = []
for line in open(dynRacesFileName):
    p = re.split(' ', line.strip())
    if (len(p) == 5):
        dynRaces.append(tuple([p[2], p[4]]))
    else:
        dynRaces.append(tuple([p[0], p[1]]))

# racePairs is a two-level dictionary. The first level key is the source location (filename:line-number) of the first
# racing access. The second level key is the source location of the second racing access.
# The value is a set of tuples racePairs_cs(x,y), where x and y are the indexes of the racing accesses in domE
 
racePairs = dict() 

# Format in racePairsFileName: 15684:weblech/spider/Spider.java:103  15717:weblech/spider/Spider.java:232
for line in open(racePairsFileName):
    access = re.split('  ', line.strip()) 
    assert (len(access) == 2)
    accFst = access[0].split(':',1)
    accSnd = access[1].split(':',1)
    innerDict = racePairs.setdefault(accFst[1], {})
    tupleSet = innerDict.setdefault(accSnd[1], set()) 
    tupleSet.add('racePairs_cs({0},{1})'.format(accFst[0], accSnd[0]))


########################################################################################################################
# 2. Extract tuples corresponding to the dynamic races and print them to outFileName
# racePairs_cs.txt contains full-path-file-names. RoadRunner sometimes gives only base file name for source location.
# Therefore, when we search for a file name (provided by RoadRunner) in racePairs_cs.txt, there is a possibility of
# multiple matches. Therefore, we need the findMatch funciton below to search the dictionary "racePairs"

def findMatch (s, d):
    keys = [key for key in d.keys() if s in key]
    return keys


with open(outFileName, 'w') as outFile:
    for dr in dynRaces:
        tupSet = set()
        keys1 = []
        keys2 = []
        keys3 = []
        keys4 = []
        keys1 = findMatch(dr[0], racePairs)
        if len(keys1) > 0:
            innerDicts = [racePairs[k] for k in keys1]
            for d in innerDicts:
                keys2 = findMatch(dr[1], d)
                for k in keys2:
                    tupSet |= d[k]
        keys3 = findMatch(dr[1], racePairs)
        if len(keys3) > 0:
            innerDicts = [racePairs[k] for k in keys3]
            for d in innerDicts:
                keys4 = findMatch(dr[0], d)
                for k in keys4:
                    tupSet |= d[k]
        if debugFlag == "dbg":
            outFile.write("Race: {0} {1}\n".format(dr[0], dr[1]))
            outFile.write("Keys1: {0}\n".format(keys1))
            outFile.write("Keys2: {0}\n".format(keys2))
            outFile.write("Keys3: {0}\n".format(keys3))
            outFile.write("Keys4: {0}\n".format(keys4))
        if len(tupSet) > 0:
            for t in tupSet: outFile.write('{0}\n'.format(t))
        if debugFlag == "dbg":
            outFile.write("\n")
    outFile.close()
