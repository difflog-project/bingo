#!/usr/bin/env python3

# Given a set of benchmarks, performs expectation maximization to learn rule weights, and produces rule-prob.txt.
# Non-determinism arises from the random choice of initial rule probabilities, and multiple runs might have to be
# performed.
# TODO! How to choose best of these runs?

# Intended to be run from the chord-fork folder.
# Arguments:
# 1. Output relation name (for e.g., racePairs_cs).
# 2. Directory in which to store temporary files and final rule-prob.txt file (for e.g., emtmp/)
# 3. Tolerance on rule probabilities before terminating (for e.g., 1e-4).
# 4. Maximum probability that is assigned to any rule (for e.g., 0.999).
# 3. Set of benchmarks on which to perform EM. Each benchmark consists of the following components:
#    a. Benchmark name (for e.g., avrora). Used only as an identifier to avoid clashes while naming temporary files.
#    b. Benchmark path (for e.g., pjbench/dacapo/benchmarks/avrora). In particular, this is assumed to contain, in the
#       proper locations, named-bnet.out, bnet-dict.out, base_queries.txt, and oracle_queries.txt.
#    c. Switch, 'augment' or 'noaugment', indicating whether the forward constraints have been augmented. This is only
#       used to determine the structure of the sub-directories.
#    d. BP-specific parameter, tolerance (0 < tolerance < 1, typically 1e-6)
#    e. BP-specific parameter, minIters
#    f. BP-specific parameter, maxIters
#    g. BP-specific parameter, histLength

# cd Error-Ranking/chord-fork
# ./scripts/bnet/em.py racePairs_cs emtmp 1e-4 0.999 \
#                      avrora pjbench/dacapo/benchmarks/avrora noaugment 1e-6 1000 1500 100 \
#                      ftp pjbench/ftp noaugment 1e-6 1000 1500 100 \
#                      hedc pjbench/hedc noaugment 1e-6 1000 1500 100

import logging
import math
import os
import random
import subprocess
import sys

########################################################################################################################
# 0. Prelude

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 1. Read input

outputRelName = sys.argv[1]
emTempDirName = sys.argv[2]
emTolerance = float(sys.argv[3])
assert 0 < emTolerance and emTolerance < 1
probMax = float(sys.argv[4])
assert 0 < probMax and probMax < 1

if (outputRelName == 'racePairs_cs'):
   analysis = 'datarace'
elif (outputRelName == 'lflow'):
   analysis = 'taint'
else:
   print('Unkown outputRelName/analysis. Exiting...')
   sys.exit()

projects = sys.argv[5:]
projects = [ projects[x:x+7] for x in range(0, len(projects), 7) ]
projects = [ { 'name': p[0], \
               'path': p[1], \
               'augSwitch': p[2], \
               'tol': float(p[3]), \
               'minIters': int(p[4]), \
               'maxIters': int(p[5]), \
               'histLength': int(p[6]) } \
             for p in projects ]

for p in projects:
    assert os.path.isdir(p['path'])
    assert 0 < p['tol'] and p['tol'] < 1
    assert 0 < p['histLength'] and p['histLength'] < p['minIters'] and p['minIters'] < p['maxIters']

    p['bnetFileName'] = '{0}'.format(p['path']) + '/chord_output_mln-{0}-problem/bnet/{1}/named-bnet.out'.format(analysis, p['augSwitch'])
    assert os.path.isfile(p['bnetFileName'])
    p['dictFileName'] = '{0}'.format(p['path']) + '/chord_output_mln-{0}-problem/bnet/{1}/bnet-dict.out'.format(analysis, p['augSwitch'])
    assert os.path.isfile(p['dictFileName'])
    p['baseQueriesFileName'] = '{0}'.format(p['path']) + '/chord_output_mln-{0}-problem/base_queries.txt'.format(analysis)
    assert os.path.isfile(p['baseQueriesFileName'])
    p['oracleQueriesFileName'] = '{0}'.format(p['path']) + '/chord_output_mln-{0}-oracle/oracle_queries.txt'.format(analysis)
    assert os.path.isfile(p['oracleQueriesFileName'])

    p['bnetLines'] = [ line.strip() for line in open(p['bnetFileName']) ]
    p['bnetLines'] = p['bnetLines'][1:]
    p['andLines'] = [ line for line in p['bnetLines'] if line.startswith('*') ]
    p['allRuleNames'] = { line.split(' ')[1] for line in p['andLines'] }
    if 'Rnarrow' in p['allRuleNames']: p['allRuleNames'].remove('Rnarrow')

    p['baseQueries'] = [ line.strip() for line in open(p['baseQueriesFileName']) ]
    p['oracleQueries'] = set([ line.strip() for line in open(p['oracleQueriesFileName']) ])

allRuleNames = { ruleName for p in projects for ruleName in p['allRuleNames'] }

for rule in allRuleNames:
    freq = 0
    for p in projects:
        freq = freq + len([ line for line in p['andLines'] if line.split(' ')[1] == rule ])
    logging.info('{0}: {1}'.format(rule, freq))

###############################
# Initialize rule probabilities
# randomSeed = 0
# random.seed(randomSeed)
# ruleProbs = { rule: 0.999 for rule in allRuleNames }
# ruleProbs = { rule: random.uniform(0.5, probMax) for rule in allRuleNames }
ruleProbs = { rule: random.uniform(0.001, probMax) for rule in allRuleNames }

def writeRuleProbs(ruleProbFileName):
    with open(ruleProbFileName, 'w') as ruleProbFile:
        for ruleName in allRuleNames:
            print('{0}: {1}'.format(ruleName, ruleProbs[ruleName]), file=ruleProbFile)
        ruleProbFile.flush()

########################################################################################################################
# 2. Run EM-loop

change = float('inf')
emIterCount = 0
# As long as the change is too large from one iteration to the next (and for one iteration at least), do...
while change > emTolerance:
    emIterCount = emIterCount + 1
    logging.info('EM iteration {0}. change: {1}.'.format(emIterCount, change))
    for rule in allRuleNames: logging.info('{0}: {1}'.format(rule, ruleProbs[rule]))

    ruleProbFileName = '{0}/rule-prob-{1}.txt'.format(emTempDirName, emIterCount)
    writeRuleProbs(ruleProbFileName)

    factorOne = { rule: 0 for rule in allRuleNames }
    factorTot = { rule: 0 for rule in allRuleNames }

    for project in projects:
        fgFileName = '{0}/factor-graph-{1}-{2}.fg'.format(emTempDirName, project['name'], emIterCount)
        bnet2FGLogFileName = '{0}/bnet2fg-{1}-{2}.log'.format(emTempDirName, project['name'], emIterCount)
        subprocess.call('./scripts/bnet/bnet2fg.py {0} {1} < {2} > {3} 2> {4}'.format(ruleProbFileName, \
                                                                                      probMax, \
                                                                                      p['bnetFileName'], \
                                                                                      fgFileName, \
                                                                                      bnet2FGLogFileName), \
                        shell=True)

        driverCmd = ['./scripts/bnet/driver.py', outputRelName, p['dictFileName'], fgFileName, p['oracleQueriesFileName']]
        with subprocess.Popen(driverCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True) as driverProc:
            driverProcStdin = driverProc.stdin
            driverProcStdout = driverProc.stdout

            def bp():
                print('BP {0} {1} {2} {3}'.format(p['tol'], p['minIters'], p['maxIters'], p['histLength']), file=driverProcStdin)
                driverProcStdin.flush()
                return driverProcStdout.readline().strip()

            def clamp(t):
                ground = 'true' if t in p['oracleQueries'] else 'false'
                print('O {0} {1}'.format(t, ground), file=driverProcStdin)
                driverProcStdin.flush()
                return driverProcStdout.readline().strip()

            def fq(clauseIndex, valIndex):
                print('FQ {0} {1}'.format(clauseIndex, valIndex), file=driverProcStdin)
                driverProcStdin.flush()
                return float(driverProcStdout.readline().strip())

            for t in p['baseQueries']: clamp(t)
            bp()
            driverProcStdin.flush()

            for clauseIndex in range(0, len(p['bnetLines'])):
                line = p['bnetLines'][clauseIndex]
                if line.startswith('+'): continue
                assert line.startswith('*')
                components = line.split(' ')
                rule = components[1]
                if rule == 'Rnarrow': continue
                assert rule in allRuleNames, 'Mysterious rule {0} not present in allRuleNames. Project is {1}.'.format(rule, project)
                assert rule in factorOne, 'Mysterious rule {0} not present in factorOne. Project is {1}.'.format(rule, project)
                assert rule in factorTot, 'Mysterious rule {0} not present in factorTot. Project is {1}.'.format(rule, project)

                numParents = int(components[2])
                oneIndex = int(math.pow(2, 1 + numParents)) - 1
                zeroIndex = oneIndex - 1

                zeroProb = fq(clauseIndex, zeroIndex)
                oneProb = fq(clauseIndex, oneIndex)

                if math.isfinite(zeroProb) and math.isfinite(oneProb):
                    assert 0 <= zeroProb and zeroProb <= 1
                    assert 0 <= oneProb and oneProb <= 1
                    factorOne[rule] = factorOne[rule] + oneProb
                    factorTot[rule] = factorTot[rule] + zeroProb + oneProb

                    if zeroProb + oneProb == 0:
                        allProbs = [ str(fq(clauseIndex, index)) for index in range(0, oneIndex + 1) ]
                        msg = 'Querying clause: {0}. zeroProb + oneProb = 0. allProbs: {1}.'
                        msg = msg.format(line, ' '.format(allProbs))
                        logging.warning(msg)

    change = 0
    for rule in allRuleNames:
        logging.info('Computing new probability for {0}. factorOne: {1}. factorTot: {2}.'.format(rule, \
                                                                                                 factorOne[rule], \
                                                                                                 factorTot[rule]))

        assert 0 <= factorOne[rule] and factorOne[rule] <= factorTot[rule]
        if factorTot[rule] <= 0:
            logging.warning('Cannot compute new probability for rule {0}, because factorTot == 0.'.format(rule))
            continue

        newProb = min(factorOne[rule] / factorTot[rule], probMax)
        change = max(change, abs(newProb - ruleProbs[rule]))
        ruleProbs[rule] = newProb

ruleProbFileName = '{0}/rule-prob.txt'.format(emTempDirName)
writeRuleProbs(ruleProbFileName)
