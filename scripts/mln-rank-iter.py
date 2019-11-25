#!/usr/bin/env python3

# Runs the baseline alarm carousel, based on the FSE15 alarm classifier.
# Inteded to be run from the chord-fork folder.
# Important: Remember to start Postgres before running this script, and stop it after. On Mukund's laptop, the Postgres
# server is already running, so ignore this advice.

# cd Error-Ranking/chord-fork
# ./scripts/postgres/start.sh
# ./scripts/mln-rank.py racePairs_cs ftp pjbench/ftp \
#                       pjbench/ftp/chord_output_mln-datarace-problem/base_queries.txt ground_queries.txt \
#                       feedback.mln results.txt stats.txt combined
# ./scripts/postgres/stop.sh

# Arguments:
# 1. Output relation name ('racePairs_cs' for datarace analysis or 'lflow' for taint analysis)
# 2. Project name (for e.g., ftp)
# 3. Project path (for e.g., pjbench/ftp)
# 4. Base queries file name, which contains list of alarms to be ranked (for e.g., base_queries.txt)
# 5. Oracle file name, which contains oracle data (for e.g., oracle_queries.txt or ground_queries.txt)
# 6. Feedback file name, for temporarily storing feedback provided to Nichrome (for e.g., feedback.mln)
# 7. Results file name, for temporarily storing results computed by Nichrome (for e.g., results.txt)
# 8. Output file name, in which to store statistics (for e.g., stats.txt)
# 9. Directory in which to place combined files, 0.out, 1.out, 2.out, ...

import logging
import os
import random
import subprocess
import time
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 0. Prelude

outputRelationName, projectName, projectPath, \
baseQueriesFileName, oracleQueriesFileName, \
feedbackFileName, resultFileName, outputFileName, combinedDirName = sys.argv[1:]

nichromeScript = './scripts/list-nichrome.sh'
solver = 'lbx' # or 'exact'

flagDict = { 'racePairs_cs': { 'analysis': 'datarace' }, \
             'lflow': { 'analysis': 'taint' } }

assert outputRelationName in flagDict, 'Unkown outputRelationName / analysis!'
analysis = flagDict[outputRelationName]['analysis']

baseQueries = { line.strip() for line in open(baseQueriesFileName) if len(line.strip()) > 0 }
oracleQueries = { line.strip() for line in open(oracleQueriesFileName) if len(line.strip()) > 0 }
assert oracleQueries.issubset(baseQueries)

if not os.path.exists(combinedDirName): os.mkdir(combinedDirName)
assert os.path.isdir(combinedDirName)

########################################################################################################################
# 1. Run the MLN alarm carousel

labelledTuples = set()
posLabelledTuples = set()
negLabelledTuples = set()

mlnClassPosTuples = baseQueries
mlnClassNegTuples = set()

with open(outputFileName, 'w') as outputFile:
    print('Tuple\tGround\tNumTrue\tNumFalse\tFraction\tExpInversionCount\tMLNNumPos\tMLNNumNeg\tPrecision\tRecall\tTime(s)', \
          file=outputFile)
    outputFile.flush()

    # Two options exist for the loop. Here is option 1, which we do not use:
    # While there exists an alarm t, such that a in mlnClassPosTuples, but t not in labelledTuples:
    # i.e. While mlnClassPosTuples is not a subset of labelledTuples:

    # while not mlnClassPosTuples.issubset(labelledTuples):
    #     # We choose t uniformly at random from the available choices.
    #     t = random.choice(list(mlnClassPosTuples - labelledTuples))
    #     # The alarm t is marked positive by the MLN, but is still uninspected by the user.

    # Here is option 2:
    # While there is an unlabelled alarm, choosing with priority from mlnClassPosTuples

    # SRK: 15th Feb 2018: for artifact evaluation.
    # while len(labelledTuples) < len(baseQueries):
    while not (oracleQueries.issubset(labelledTuples)):
        unlabelledTuples = [ (t, random.uniform(0.5, 1)) for t in mlnClassPosTuples if t not in labelledTuples ] + \
                           [ (t, random.uniform(0, 0.5)) for t in mlnClassNegTuples if t not in labelledTuples ]
        unlabelledTuples = sorted(unlabelledTuples, key=lambda pair: -pair[1])
        t = unlabelledTuples[0][0]
        assert t not in labelledTuples

        # We print the combined.out file
        allTuples = [ (t, 1) for t in posLabelledTuples] + unlabelledTuples + [ (t, 0) for t in negLabelledTuples ]
        combinedFileName = '{0}.out'.format(len(posLabelledTuples) + len(negLabelledTuples))
        combinedFileName = os.path.join(combinedDirName, combinedFileName)
        with open(combinedFileName, 'w') as combinedFile:
            print('Rank\tConfidence\tGround\tLabel\tComments\tTuple', file=combinedFile)
            index = 0
            for tp, tpConfidence in allTuples:
                index = index + 1
                ground = 'TrueGround' if tp in oracleQueries else 'FalseGround'
                label = 'PosLabel' if tp in posLabelledTuples else \
                        'NegLabel' if tp in negLabelledTuples else \
                        'Unlabelled'
                print('{0}\t{1}\t{2}\t{3}\tSPOkGoodGood\t{4}'.format(index, tpConfidence, ground, label, tp), file=combinedFile)

        # We present t to the user for inspection:
        labelledTuples.add(t)
        if t in oracleQueries: posLabelledTuples.add(t)
        else: negLabelledTuples.add(t)

        # We compute some statistics
        groundStr = 'TrueGround' if t in oracleQueries else 'FalseGround'
        numPos = len(posLabelledTuples)
        numNeg = len(negLabelledTuples)
        fracPos = numPos / (numPos + numNeg)
        mlnNumPos = len(mlnClassPosTuples)
        mlnNumNeg = len(mlnClassNegTuples)

        po = mlnClassPosTuples & oracleQueries
        pno = mlnClassPosTuples - po
        no = mlnClassNegTuples & oracleQueries
        nno = mlnClassNegTuples - no
        expInversionCount = (len(po) * len(pno) / 2) + (len(no) * len(nno) / 2) + (len(pno) * len(no))

        precision = len(po) / len(mlnClassPosTuples) if len(mlnClassPosTuples) > 0 else 1
        recall = len(po) / len(oracleQueries)

        with open(feedbackFileName, 'w') as feedbackFile:
            for tp in posLabelledTuples: print('{0}.'.format(tp), file=feedbackFile)
            for tp in negLabelledTuples: print('!{0}.'.format(tp), file=feedbackFile)
            feedbackFile.flush()

        startTime = time.time()
        subprocess.call([nichromeScript, projectName, projectPath, analysis, solver, \
                                         feedbackFileName, resultFileName, 'nopopups'])
        endTime = time.time()
        procTime = int(endTime - startTime)

        print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}'.format(t, groundStr, numPos, numNeg, \
                                                                        fracPos, expInversionCount, \
                                                                        mlnNumPos, mlnNumNeg, \
                                                                        precision, recall, procTime), \
              file=outputFile)
        outputFile.flush()

        resultLines = [ line.strip() for line in open(resultFileName) ]
        mlnClassPosTuples = { tp.strip() for tp in resultLines } & baseQueries
        mlnClassNegTuples = baseQueries - mlnClassPosTuples
        break
