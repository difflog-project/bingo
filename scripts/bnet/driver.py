#!/usr/bin/env python3

# Accepts human-readable commands from stdin, and passes them to LibDAI/wrapper.cpp, thus acting as a convenient driver.
# Arguments:
# 1. Dictionary file for the bayesian network, named-dict.out, produced by cons_all2bnet.py. This is to translate
#    commands, such as "O racePairs_cs(428,913) true" to the format accepted by LibDAI/wrapper.cpp, such as
#    "O 38129 true".
# 2. Factor graph, factor-graph.fg
# 3. Base queries file, base_queries.txt. This need not be the full list of base queries produced by Chord, but could
#    instead be any subset of it, such as the alarms reported by the upper oracle.
# 4. Oracle queries file, oracle_queries.txt. Needed while producing combined.out.

# Intended to be run from the main Bingo directory
# ./scripts/bnet/driver.py pjbench/ftp/bnet/noaugment/bnet-dict.out \
#                          pjbench/ftp/bnet/noaugment/factor-graph.fg \
#                          pjbench/ftp/base_queries.txt \
#                          pjbench/ftp/oracle_queries.txt

import logging
import math
import subprocess
import sys
import time
import re
import rankv2

dictFileName = sys.argv[1]
fgFileName = sys.argv[2]
baseQueriesFileName = sys.argv[3]
oracleQueriesFileName = sys.argv[4]
rankv2.load()

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
for q in oracleQueries: assert q in baseQueries, f'Oracle query {q} not found in baseQueries'
for q in baseQueries: assert q in bnetDict, f'Base query {q} not found in bnetDict'

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

    def unobserve(t):
        assert t in labelledTuples, f'Attempting to unobserve already unobserved variable {t}'
        execWrapperCmd(f'UC {bnetDict[t]}')
        del labelledTuples[t]

    def getRankedAlarms():
        alarmList = []
        for t in baseQueries:
            index = bnetDict[t]
            response = float(execWrapperCmd('Q {0}'.format(index)))
            alarmList.append((t, response))
        def getLabelInt(t): return 0 if t not in labelledTuples else 1 if labelledTuples[t] else -1
        def sortKey(rec):
            confidence = rec[1] if not math.isnan(rec[1]) else 0
            return (-confidence, -rankv2.get_weight(rec[0]))
            #return (-getLabelInt(rec[0]), -confidence, not math.isnan(rec[1]), rec[0])
        return sorted(alarmList, key=sortKey)

    def getRankedTuples():
        tupleList = []
        for t, index in bnetDict.items():
            if ' ' not in t:
                response = float(execWrapperCmd(f'Q {index}'))
                tupleList.append((t, response))
        def getLabelInt(t): return 0 if t not in labelledTuples else 1 if labelledTuples[t] else -1
        def sortKey(rec):
            confidence = rec[1] if not math.isnan(rec[1]) else 0
            return (-getLabelInt(rec[0]), -confidence, not math.isnan(rec[1]), rec[0])
        return sorted(tupleList, key=sortKey)

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

    def printMRankedAlarms(outFile):
        alarmList = getRankedAlarms()
        print('Rank\tConfidence\tLabel\tTuple', file=outFile)
        index = 0
        for t, confidence in alarmList:
            index = index + 1
            label = 'Unlabelled' if t not in labelledTuples else \
                    'PosLabel' if labelledTuples[t] else \
                    'NegLabel'
            print(f'{index}\t{confidence}\t{label}\t{t}', file=outFile)

    def printRankedTuples(outFile):
        alarmList = getRankedTuples()
        print('Rank\tConfidence\tGround\tLabel\tComments\tTuple', file=outFile)
        index = 0
        for t, confidence in alarmList:
            index = index + 1
            ground = 'TrueGround' if t in oracleQueries else 'FalseGround'
            label = 'Unlabelled' if t not in labelledTuples else \
                    'PosLabel' if labelledTuples[t] else \
                    'NegLabel'
            print(f'{index}\t{confidence}\t{ground}\t{label}\tSPOkGoodGood\t{t}', file=outFile)

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

    def runManualAlarmCarousel(tolerance, minIters, maxIters, histLength, statsFile, combinedPrefix, combinedSuffix):
        assert 0 < tolerance and tolerance < 1
        assert 0 < histLength and histLength < minIters and minIters < maxIters

        numTrue = 0
        numFalse = 0

        print('Tuple\tConfidence\tGround\tNumTrue\tNumFalse\tFraction\tYetToConvergeFraction\tTime(s)', file=statsFile)
        while len(labelledTuples) < len(baseQueries):
            startTime = time.time()
            yetToConvergeFraction = float(execWrapperCmd('BP {0} {1} {2} {3}'.format(tolerance, minIters, maxIters, histLength)))
            rankedAlarmList = getRankedAlarms()
            unlabelledAlarms = [ (t, confidence) for t, confidence in rankedAlarmList if t not in labelledTuples ]
            t0, conf0 = unlabelledAlarms[0]
            endTime = time.time()
            thisTime = int(endTime - startTime)

            print(f'Highest ranked alarm: {t0} (confidence = {conf0}). Real bug (Y) / False alarm (N) / Abort (A)?')
            ground = next(sys.stdin).strip()
            if ground == 'A':
                logging.info('Aborting MAC interaction loop.')
                break
            ground = (ground == 'Y')
            if ground:
                ground = 'TrueGround'
                numTrue = numTrue + 1
            else:
                ground = 'FalseGround'
                numFalse = numFalse + 1
            fraction = numTrue / (numTrue + numFalse)
            print(f'{t0}\t{conf0}\t{ground}\t{numTrue}\t{numFalse}\t{fraction}\t{yetToConvergeFraction}\t{thisTime}', \
                  file=statsFile)
            statsFile.flush()

            with open(f'{combinedPrefix}{numTrue + numFalse - 1}.{combinedSuffix}', 'w') as outFile:
                printMRankedAlarms(outFile)

            logging.info('Setting tuple {0} to value {1}'.format(t0, t0 in oracleQueries))
            observe(t0, t0 in oracleQueries)

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
            result = float(execWrapperCmd(fwdCmd))
            logging.info(f'Pr({t} | evidence) = {result}')
            print(f'{t} {result}')

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

        elif cmdType == 'UC':
            # 2f. Unobserve previously observed tuples.
            # Syntax: UC t.
            # Requires that t have been previously observed.
            # Output: 'UC t'. Merely an acknowledgment of unobservation.
            # Experimental feature, to eliminate troublesome NaNs.
            t, = components
            unobserve(t)
            print(f'UC {t}')

        elif cmdType == 'P':
            # 2g. Printing ranked list of alarms to file
            # Syntax: P filename.
            # Output: Ranked list of alarms, in the format of combined.out. Printed to filename. Acknowledgment printed
            # to stdout.
            outFileName = components[0]
            with open(outFileName, 'w') as outFile: printRankedAlarms(outFile)
            print('P {0}'.format(outFileName))

        elif cmdType == 'PT':
            # 2h. Printing ranked list of tuples to file
            # Syntax: PT filename.
            # Output: Ranked list of tuples, in the format of combined.out. Printed to filename. Acknowledgment printed
            # to stdout.
            outFileName = components[0]
            with open(outFileName, 'w') as outFile: printRankedTuples(outFile)
            print('PT {0}'.format(outFileName))

        elif cmdType == 'HA':
           # 2i. Get the alarm with the highest ranking and maximum confidence.
           # Syntax: HA.
           # Output: A tuple t
           alarmList = getRankedAlarms()
           topAlarm, confidence = alarmList[0]
           groundTruth = 'TrueGround' if topAlarm in oracleQueries else 'FalseGround'
           logging.info(f'Top ranked alarm: {topAlarm} (confidence = {confidence}).')
           print('{0} {1} {2}'.format(topAlarm, confidence, groundTruth))

        elif cmdType == 'AC':
            # 2j. Run alarm carousel
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

        elif cmdType == 'MAC':
            # 2k. Run a manual alarm carousel
            # Syntax: MAC tolerance minIters maxIters histLength statsFileName combinedPrefix combinedSuffix.
            # Output Alarm carousel statistics, in the format of stats.txt, printed to statsFileName. Static ranked
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
                runManualAlarmCarousel(tolerance, minIters, maxIters, histLength, statsFile, combinedPrefix, combinedSuffix)

        else:
            assert cmdType == 'NL', 'Unexpected command {0}!'.format(command)
            print()

        sys.stdout.flush()
        logging.info('Awaiting command')

logging.info('Bye!')
