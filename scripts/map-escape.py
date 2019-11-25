#!/usr/bin/env python3
#
# Should be run from chord-fork folder
# Args:
#  map-escape.py <folder-containing-the-bddbddb-dir-for-app> <file-containing-esc-query-ndx> <output-file>
#
#  example:
#  map-escape.py $PROGRAM_PATH/chord_output_thresc_metaback/Master \
#                $PROGRAM_PATH/chord_output_thresc_metaback/Master/proven_queries.txt \
#                $PROGRAM_PATH/proven_queries_mapped.txt
#

import logging
import time
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

domEDir = sys.argv[1]
provQueriesFile = sys.argv[2]
mappedQueriesFile = sys.argv[3]

domE = []
domEFile = open('{0}/bddbddb/E.map'.format(domEDir),'r')
for line in domEFile.readlines():
    line = line.strip()
    domE.append(line)
domEFile.close()

provenQueries = open(provQueriesFile,'r')
notThrEsc = []
for line in provenQueries.readlines():
    line = line.strip()
    notThrEsc.append(int(line))
provenQueries.close()

provQMapped = open(mappedQueriesFile,'w')
for e in notThrEsc:
    provQMapped.write(str(domE[e])+'\n')
provQMapped.close()
