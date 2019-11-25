#!/usr/bin/env python3

import os
import subprocess
import sys

program = sys.argv[1]
programPath = sys.argv[2]
satSolver = sys.argv[3] # 'lbx' or 'mcsls' for approximate solvers, or 'exact' for exact solving
prefixFilter = sys.argv[4] # 'racePairs_cs' for datarace analysis

def readlines(fname):
    return [ line.strip() for line in open(fname) if line.strip().startswith(prefixFilter) ]

oracleBase = os.path.join(programPath, 'chord_output_mln-datarace-oracle')
problemBase = os.path.join(programPath, 'chord_output_mln-datarace-problem')

oracleTuples = set(readlines(os.path.join(oracleBase, 'oracle_queries.txt')))
baseTuples = set(readlines(os.path.join(problemBase, 'base_queries.txt')))

def processFeedbackFile(feedbackFileName):
    feedbackLevelIndex = feedbackFileName.rfind('infFeedback_') + len('infFeedback_')
    feedbackLevel = feedbackFileName[feedbackLevelIndex:-4]

    problemEDB = os.path.join(problemBase, 'problem.edb')
    resultFileName = os.path.join(problemBase, 'result-{0}.txt'.format(feedbackLevel))
    inputFiles = '{0},{1},{2}'.format('./mln_bench/program_analyses/datarace.mln', \
                                      './chord_incubator/src/chord/analyses/mln/rev_or.mln', \
                                      feedbackFileName)
    revertedConsTxt = os.path.join(problemBase, 'reverted_cons_all.txt')
    consAll = os.path.join(problemBase, 'cons_all.txt')
    outputFileName = os.path.join(problemBase, 'output-{0}.txt'.format(feedbackLevel))
    try:
        with open(outputFileName, 'w') as outputFile:
            subprocess.call(['java', '-Xmx24g', \
                                     '-jar', './nichrome/nichrome/main/nichrome.jar', \
                                     'MLN', \
                                     '-conf', './nichrome/nichrome/Nichrome.conf', \
                                     '-e', problemEDB, \
                                     '-r', resultFileName, \
                                     '-i', inputFiles, \
                                     '-loadrev', revertedConsTxt, \
                                     '-loadgc', consAll, \
                                     '-verbose', '2', \
                                     '-ignoreWarmGCWeight', \
                                     '-solver', satSolver, \
                                     '-lbxTimeout', '180', \
                                     '-lbxLimit', '1', \
                                     '-printVio', \
                                     '-fullyGround'], \
                            timeout=1200, stdin=None, stdout=outputFile, stderr=outputFile)

        mlnTuples = set(readlines(resultFileName))
        truePositives = mlnTuples & oracleTuples
        falsePositives = mlnTuples - oracleTuples
        falseNegatives = oracleTuples - mlnTuples
        mysteriousTuples = mlnTuples - baseTuples
        print('{0}\t{1}\t{2}\t{3}\t{4}'.format(feedbackLevel, \
                                               len(truePositives), \
                                               len(falsePositives), \
                                               len(falseNegatives), \
                                               len(mysteriousTuples)))
    except subprocess.SubprocessError as err:
        print(err)

with open(os.path.join(problemBase, 'infFeedback_0.mln'), 'w') as zeroFeedbackFile:
    pass

subprocess.call(['./scripts/postgres/start.sh'])
print('Feedback\tTruePositives\tFalsePositives\tFalseNegatives\t|mln-base|')
for feedbackFileName in os.listdir(problemBase):
    if feedbackFileName.startswith('infFeedback_'):
        processFeedbackFile(os.path.join(programPath, 'chord_output_mln-datarace-problem', feedbackFileName))
subprocess.call(['./scripts/postgres/stop.sh'])
