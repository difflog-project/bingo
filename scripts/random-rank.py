#!/usr/bin/env python3

# Runs the baseline alarm carousel, based on a random ranker.

# cd Error-Ranking/chord-fork
# ./scripts/random-rank.py pjbench/ftp/chord_output_mln-datarace-problem/base_queries.txt \
#                          pjbench/ftp/chord_output_mln-datarace-oracle/oracle_queries.txt \
#                          combined \
#                          stats.txt

# Arguments:
# 1. List of base queries, i.e. of all alarms
# 2. List of oracle queries, i.e. those alarms which are true
# 3. Directory in which to place the combined .out files, 0.out, 1.out, 2.out, ...
# 4. Name of file in which to place ranking statistics, stats.txt

import logging
import os
import random
import time
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 0. Prelude

baseQueriesFileName, oracleQueriesFileName, combinedDirName, statsFileName = sys.argv[1:]

baseQueries = { line.strip() for line in open(baseQueriesFileName) }
oracleQueries = { line.strip() for line in open(oracleQueriesFileName) }
assert oracleQueries.issubset(baseQueries)

if not os.path.exists(combinedDirName): os.mkdir(combinedDirName)
assert os.path.isdir(combinedDirName)

logging.info('Loaded {0} base queries.'.format(len(baseQueries)))
logging.info('Loaded {0} oracle queries.'.format(len(oracleQueries)))

########################################################################################################################
# 1. Run alarm carousel

labelledTrue = set()
labelledFalse = set()
unlabelledQueries = set(baseQueries)

with open(statsFileName, 'w') as statsFile:
    print('Tuple\tGround\tNumTrue\tNumFalse\tFraction\tExpInversionCount', file=statsFile)

    while len(unlabelledQueries) > 0:
        confidences = [ (t, random.random()) for t in unlabelledQueries ]
        confidences = sorted(confidences, key=lambda pair: -pair[1])
        t, tConfidence = confidences[0]
        confidences = [ (t, 1) for t in labelledTrue ] + confidences + [ (t, 0) for t in labelledFalse ]

        if t in oracleQueries: labelledTrue.add(t)
        else: labelledFalse.add(t)
        unlabelledQueries.remove(t)

        ground = 'TrueGround' if t in oracleQueries else 'FalseGround'
        numTrue = len(labelledTrue)
        numFalse = len(labelledFalse)
        fraction = numTrue / (numTrue + numFalse)

        numUnlabelledTrue = len(unlabelledQueries & oracleQueries)
        numUnlabelledFalse = len(unlabelledQueries - oracleQueries)
        expInversionCount = numUnlabelledTrue * numUnlabelledFalse / 2

        print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(t, ground, numTrue, numFalse, fraction, expInversionCount), \
              file=statsFile)

        combinedFileName = os.path.join(combinedDirName, '{0}.out'.format(numTrue + numFalse - 1))
        with open(combinedFileName, 'w') as combinedFile:
            print('Rank\tConfidence\tGround\tLabel\tComments\tTuple', file=combinedFile)
            index = 0
            for tp, tpConfidence in confidences:
                index = index + 1
                ground = 'TrueGround' if tp in oracleQueries else 'FalseGround'
                label = 'PosLabel' if tp in labelledTrue else \
                        'NegLabel' if tp in labelledFalse else \
                        'Unlabelled'
                print('{0}\t{1}\t{2}\t{3}\tSPOkGoodGood\t{4}'.format(index, tpConfidence, ground, label, tp), file=combinedFile)
