#!/usr/bin/env python3

# Given a bnet.out file produced by cons_all2bnet.py, and a rule-prob.txt file mapping each rule to its probability of
# firing, this script produces a factorGraph.fg file accepted by LibDAI.

# The default probability is the probability assigned to any rule not found in rule-prob.txt, and the leak is the amount
# by which and and or gates diverge from their deterministic counterparts. Ideally, leak = 0.

# ./bnet2fg.py ruleProb.txt 0.99 0.01 < named_bnet.out > factorGraph.fg 2> bnet2fg.log

import logging
import math
import subprocess
import sys

ruleProbFileName = sys.argv[1]
defaultProbability = float(sys.argv[2])
leak = float(sys.argv[3])

assert 0 <= defaultProbability and defaultProbability <= 1
assert 0 <= leak and leak <= 1

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 1. Accept input

# Read bayesian network
bnetLines = [ line.strip() for line in sys.stdin ]

# Load rule probabilities
ruleProbs = [ line.strip().split(': ') for line in open(ruleProbFileName) ]
ruleProbs = { line[0]: float(line[1]) for line in ruleProbs }

########################################################################################################################
# 2. Compute output

# https://staff.fnwi.uva.nl/j.m.mooij/libDAI/doc/fileformats.html
# It starts with a line containing the number of factors in that graph, followed by an empty line.
numVars = int(bnetLines[0])

outLines = [ numVars, '' ]
logging.info(numVars)
logging.info('')
print(numVars)
print('')

factorLines = bnetLines[1:(numVars + 1)]
assert len(factorLines) == numVars
for varIndex in range(numVars):
    outLines = []
    # Then all factors are specified, using one block for each factor,

    line = factorLines[varIndex]
    components = [ c.strip() for c in line.split(' ') ]

    factorType = components[0] # '*' or '+'
    assert factorType == '*' or factorType == '+'
    ruleName = components[1] if factorType == '*' else None
    numParents = int(components[2]) if factorType == '*' else int(components[1])
    parents = [ int(p) for p in components[3:] ] if factorType == '*' else [ int(p) for p in components[2:] ]

    outLines.append('# Factor {0} of {1}. Finished printing {2}% of factors.'.format(varIndex, numVars, 100 * varIndex / numVars))
    outLines.append('# {0}'.format(line))
    # Each block describing a factor starts with a line containing the number of variables in that factor.
    outLines.append(1 + numParents)
    # The second line contains the labels of these variables, seperated by spaces
    # (labels are nonnegative integers and to avoid confusion, it is suggested to start counting at 0).
    factorVars = [ varIndex ] + parents
    outLines.append(' '.join([ str(v) for v in factorVars ]))
    # The third line contains the number of possible values of each of these variables, also seperated by spaces.
    outLines.append(' '.join([ '2' for v in factorVars ]))

    if factorType == '*':
        # The fourth line contains the number of nonzero entries in the factor table.
        tableSize = int(math.pow(2, 1 + numParents))
        nonZeroEntries = tableSize # int((tableSize / 2) + 1)
        outLines.append(nonZeroEntries)

        # The rest of the lines contain these nonzero entries;
        # each line consists of a table index, followed by the value corresponding to that table index.
        # The most difficult part is getting the indexing right.
        # The convention that is used is that the left-most variables
        # cycle through their values the fastest
        # (similar to MatLab indexing of multidimensional arrays).
        for i in range(0, tableSize - 2, 2):
            # outLines.append('{0} 1'.format(i))
            outLines.append('{0} {1}'.format(i, 1 - leak))
            outLines.append('{0} {1}'.format(i + 1, leak))

        probability = ruleProbs[ruleName] if (ruleName != None and ruleName in ruleProbs) else \
                      (1 - leak) if ruleName == 'Rnarrow' else \
                      defaultProbability

        outLines.append('{0} {1}'.format(tableSize - 2, 1 - probability))
        outLines.append('{0} {1}'.format(tableSize - 1, probability))
    else:
        # The fourth line contains the number of nonzero entries in the factor table.
        tableSize = int(math.pow(2, 1 + numParents))
        nonZeroEntries = tableSize # int((tableSize / 2))
        outLines.append(nonZeroEntries)

        # outLines.append('0 1')
        outLines.append('0 {0}'.format(1 - leak))
        outLines.append('1 {0}'.format(leak))
        for i in range(3, tableSize, 2):
            # outLines.append('{0} 1'.format(i))
            outLines.append('{0} {1}'.format(i - 1, leak))
            outLines.append('{0} {1}'.format(i, 1 - leak))

    # where the blocks are seperated by empty lines.
    outLines.append('')

    # Print.
    for line in outLines:
        line = str(line)
        logging.info(line)
        if not line.startswith('#'): print(line)
