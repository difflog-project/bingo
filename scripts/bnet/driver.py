#!/usr/bin/env python3

# Intended to be run from the chord-fork folder.
# cd Error-Ranking/chord-fork
# ./scripts/bnet/driver.py pjbench/ftp/chord_output_mln-datarace-problem/bnet/noaugment/bnet-dict.out \
#                          pjbench/ftp/chord_output_mln-datarace-problem/bnet/noaugment/factor-graph.fg \
#                          pjbench/ftp/chord_output_mln-datarace-problem/base_queries.txt \
#                          pjbench/ftp/chord_output_mln-datarace-oracle/oracle_queries.txt

# Accepts human-readable commands from stdin, and passes them to LibDAI/wrapper.cpp, thus acting as a convenient driver.
# Arguments:
# 1. Dictionary file for the bayesian network, named-dict.out, produced by cons_all2bnet.py. This is to translate
#    commands, such as "O racePairs_cs(428,913) true" to the format accepted by LibDAI/wrapper.cpp, such as
#    "O 38129 true".
# 2. Factor graph, factor-graph.fg
# 3. Base queries file, base_queries.txt. This need not be the full list of base queries produced by Chord, but could
#    instead be any subset of it, such as the alarms reported by the upper oracle.
# 4. Oracle queries file, oracle_queries.txt. Needed while producing combined.out.

import logging
import subprocess
import sys
import time
import re

dictFileName = sys.argv[1]
fgFileName = sys.argv[2]
baseQueriesFileName = sys.argv[3]
oracleQueriesFileName = sys.argv[4]

wrapperExecutable = './libdai/wrapper'

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 1. Setup

# 1a. Populate bayesian network node dictionary
bnetDict = {}
for line in open(dictFileName):
    line = line.strip()
    if len(line) == 0: continue
    components = [ c.strip() for c in line.split(': ') if len(c.strip()) > 0 ]
    assert len(components) == 2
    bnetDict[components[1]] = components[0]

# 1b. Initialize set of labelled tuples (to confirm that tuples are not being relabelled), and populate the set of
# alarms in the ground truth.
labelledTuples = {}

oracleQueries = set([ line.strip() for line in open(oracleQueriesFileName) if len(line.strip()) > 0 ])
baseQueries = set([ line.strip() for line in open(baseQueriesFileName) if len(line.strip()) > 0 ])
assert(oracleQueries.issubset(baseQueries))
assert(baseQueries.issubset(set(bnetDict.keys())))

logging.info('Populated {0} oracle queries.'.format(len(oracleQueries)))
logging.info('Populated {0} base queries.'.format(len(baseQueries)))

# SRK: 15 Feb 2018: For artifact evaluation
unoptimizedRun = 1 if ("noaugment_unopt" in fgFileName) else 0

########################################################################################################################
# 2. Start LibDAI/wrapper.cpp, and interact with the user

with subprocess.Popen([wrapperExecutable, fgFileName], \
                      stdin=subprocess.PIPE, \
                      stdout=subprocess.PIPE, \
                      universal_newlines=True) as wrapperProc:

    def execWrapperCmd(fwdCmd):
        logging.info('Driver to wrapper: ' + fwdCmd)
        print(fwdCmd, file=wrapperProc.stdin)
        wrapperProc.stdin.flush()
        response = wrapperProc.stdout.readline().strip()
        logging.info('Wrapper to driver: ' + response)
        return response

    def observe(t, value):
        assert t not in labelledTuples, 'Attempting to relabel alarm {0}'.format(t)
        if not value == (t in oracleQueries):
            logging.warning('Labelling alarm {0} with value {1}, which does not match ground truth.'.format(t, value))

        fwdCmd = 'O {0} {1}'.format(bnetDict[t], 'true' if value else 'false')
        execWrapperCmd(fwdCmd)
        labelledTuples[t] = value

    def getRankedAlarms():
        alarmList = []
        for t in baseQueries:
            index = bnetDict[t]
            response = float(execWrapperCmd('Q {0}'.format(index)))
            alarmList.append((t, response))
        def getLabelInt(t): return 0 if t not in labelledTuples else 1 if labelledTuples[t] else -1
        return sorted(alarmList, key=lambda rec: (-getLabelInt(rec[0]), -rec[1], rec[0]))

    def getInversionCount(alarmList):
        numInversions = 0
        numFalse = 0
        for t, confidence in alarmList:
            if t in oracleQueries: numInversions = numInversions + numFalse
            else: numFalse = numFalse + 1
        return numInversions

    def printRankedAlarms(outFile):
        alarmList = getRankedAlarms()
        print('Rank\tConfidence\tGround\tLabel\tComments\tTuple', file=outFile)
        index = 0
        for t, confidence in alarmList:
            index = index + 1
            ground = 'TrueGround' if t in oracleQueries else 'FalseGround'
            label = 'Unlabelled' if t not in labelledTuples else \
                    'PosLabel' if labelledTuples[t] else \
                    'NegLabel'
            print('{0}\t{1}\t{2}\t{3}\tSPOkGoodGood\t{4}'.format(index, confidence, ground, label, t), file=outFile)

    def runAlarmCarousel(tolerance, minIters, maxIters, histLength, statsFile, combinedPrefix, combinedSuffix):
        assert 0 < tolerance and tolerance < 1
        assert 0 < histLength and histLength < minIters and minIters < maxIters

        numTrue = 0
        numFalse = 0

        print('Tuple\tConfidence\tGround\tNumTrue\tNumFalse\tFraction\tInversionCount\tYetToConvergeFraction\tTime(s)', file=statsFile)
        lastTime = time.time()
        #while len(labelledTuples) < len(baseQueries):
        # SRK: 15th Feb 2018: for artifact evaluation.
        startTime = time.time()
        while not (oracleQueries.issubset(labelledTuples.keys())):
            yetToConvergeFraction = float(execWrapperCmd('BP {0} {1} {2} {3}'.format(tolerance, minIters, maxIters, histLength)))
            rankedAlarmList = getRankedAlarms()
            unlabelledAlarms = [ (t, confidence) for t, confidence in rankedAlarmList if t not in labelledTuples ]
            t0, conf0 = unlabelledAlarms[0]

            ground = 'TrueGround' if t0 in oracleQueries else 'FalseGround'
            if t0 in oracleQueries: numTrue = numTrue + 1
            else: numFalse = numFalse + 1
            fraction = numTrue / (numTrue + numFalse)
            inversionCount = getInversionCount(rankedAlarmList)
            thisTime = int(time.time() - lastTime)
            lastTime = time.time()
            print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}'.format(t0, conf0, ground, numTrue, numFalse, fraction, \
                                                                       inversionCount, yetToConvergeFraction, thisTime), \
                  file=statsFile)
            statsFile.flush()

            with open('{0}{1}.{2}'.format(combinedPrefix, numTrue + numFalse - 1, combinedSuffix), 'w') as outFile:
                printRankedAlarms(outFile)

            logging.info('Setting tuple {0} to value {1}'.format(t0, t0 in oracleQueries))
            observe(t0, t0 in oracleQueries)
            # SRK: 15th Feb 2018: for artifact evaluation.
            if (unoptimizedRun == 1):
                if (len(labelledTuples.keys()) == 4) or ((time.time() - startTime) > 14400):
                    break

    logging.info('Awaiting command')
    for command in sys.stdin:
        command = command.strip()
        logging.info('Read command {0}'.format(command))

        components = [ c.strip() for c in re.split(' |\t', command) if len(c.strip()) > 0 ]
        if len(components) == 0: continue

        cmdType = components[0]
        components = components[1:]

        if cmdType == 'Q':
            # 2a. Marginal probability query.
            # Syntax: Q t.
            # Output: t belief(t).
            t = components[0]
            fwdCmd = 'Q {0}'.format(bnetDict[t])
            print('{0} {1}'.format(t, float(execWrapperCmd(fwdCmd))))

        elif cmdType == 'FQ':
            # 2b. Factor marginal.
            # Syntax: FQ f i.
            # Output: belief(f, i).
            # Note: No encoding or decoding is performed for this command. It is intended to be used by em.py, which can
            # do these things on its own.
            print(float(execWrapperCmd(command)))

        elif cmdType == 'BP':
            # 2c. Run belief propagation.
            # Syntax: BP tolerance minIters maxIters histLength.
            # Output: 'converged' if belief propagation converged, or 'diverged' otherwise.
            tolerance = float(components[0])
            minIters = int(components[1])
            maxIters = int(components[2])
            histLength = int(components[3])

            assert 0 < tolerance and tolerance < 1
            assert 0 < histLength and histLength < minIters and minIters < maxIters

            print(execWrapperCmd('BP {0} {1} {2} {3}'.format(tolerance, minIters, maxIters, histLength)))

        elif cmdType == 'OO':
            # 2d. Observe oracle data. Read tuple and infer value from oracle_queries.txt
            # Syntax: OO t.
            # Output: 'O t value'. Value assigned to the tuple. Merely an acknowledgment that the command was received.
            t = components[0]
            value = t in oracleQueries
            observe(t, value)
            print('O {0} {1}'.format(t, 'true' if value else 'false'))

        elif cmdType == 'O':
            # 2e. Observe oracle data.
            # Syntax: O t value.
            # Output: 'O t value'. Merely an acknowledgment that the command was received.
            t = components[0]
            assert components[1] == 'true' or components[1] == 'false'
            value = (components[1] == 'true')
            observe(t, value)
            print('O {0} {1}'.format(t, 'true' if value else 'false'))

        elif cmdType == 'P':
            # 2f. Printing ranked list of alarms to file
            # Syntax: P filename.
            # Output: Ranked list of alarms, in the format of combined.out. Printed to filename. Acknowledgment printed
            # to stdout.
            outFileName = components[0]
            with open(outFileName, 'w') as outFile: printRankedAlarms(outFile)
            print('P {0}'.format(outFileName))

        elif cmdType == 'HA':
           # 2g. Get the alarm with the highest ranking and maximum confidence.
           # Syntax: HA.
           # Output: A tuple t
           alarmList = getRankedAlarms()
           topAlarm, confidence = alarmList[0]
           groundTruth = 'TrueGround' if topAlarm in oracleQueries else 'FalseGround'
           print('{0} {1} {2}'.format(topAlarm, confidence, groundTruth))

        elif cmdType == 'AC':
            # 2h. Run alarm carousel
            # Syntax: AC tolerance minIters maxIters histLength statsFileName combinedPrefix combinedSuffix.
            # Output: Alarm carousel statistics, in the format of stats.txt, printed to statsFileName. Static ranked
            # list of alarms at step n, in the format of combined.out, is printed to file named
            # 'combinedPrefixn.combinedSuffix'. Nothing printed to stdout.
            tolerance = float(components[0])
            minIters = int(components[1])
            maxIters = int(components[2])
            histLength = int(components[3])

            statsFileName = components[4]
            combinedPrefix = components[5]
            combinedSuffix = components[6]

            assert 0 < tolerance and tolerance < 1
            assert 0 < histLength and histLength < minIters and minIters < maxIters

            with open(statsFileName, 'w') as statsFile:
                runAlarmCarousel(tolerance, minIters, maxIters, histLength, statsFile, combinedPrefix, combinedSuffix)

        else:
            assert cmdType == 'NL', 'Unexpected command {0}!'.format(command)
            print()

        sys.stdout.flush()
        logging.info('Awaiting command')

logging.info('Bye!')
