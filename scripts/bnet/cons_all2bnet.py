#!/usr/bin/env python3

# Given a cycle-free set of constraints on stdin, produces a bayesian network, suitable for use by bnet2fg.py, on
# stdout. Also outputs a dictionary mapping tuples and grounded clauses to node numbers, and places this in a dictioanry
# file.

# ./cons_all2bnet.py bnet-dict.out [narrowor] < named_cons_all.txt > named-bnet.out

# The output of prune-cons will work well as input to this script.

import logging
import re
import sys

dictOutFileName = sys.argv[1]

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 0. Prelude

def lit2Tuple(literal):
    return literal if not literal.startswith('NOT ') else literal[len('NOT '):]

def clause2Antecedents(clause):
    return [ lit2Tuple(literal) for literal in clause[:-1] ]

def clause2Consequent(clause):
    consequent = clause[-1]
    assert not consequent.startswith('NOT ')
    return consequent

########################################################################################################################
# 1. Accept input

allClauses = set()
allRuleNames = {}
allTuples = set()
allConsequents = set()

for line in sys.stdin:
    line = line.strip()
    clause = [ literal.strip() for literal in re.split(':|, ', line) ]
    ruleName = clause[0]
    clause = clause[1:]
    clause = tuple(clause)
    allClauses.add(clause)
    allRuleNames[clause] = ruleName

    for literal in clause:
        allTuples.add(lit2Tuple(literal))

    allConsequents.add(clause2Consequent(clause))

allInputTuples = allTuples - allConsequents

logging.info('Loaded {0} clauses.'.format(len(allClauses)))
logging.info('Discovered {0} tuples.'.format(len(allTuples)))
logging.info('Discovered {0} consequents.'.format(len(allConsequents)))
logging.info('Discovered {0} input tuples.'.format(len(allInputTuples)))

########################################################################################################################
# 2. Narrow disjunctions

# Map each tuple to the number of clauses deriving it
tuple2ConsequentClauses = { t: set() for t in allTuples }
for clause in allClauses:
    consequent = clause2Consequent(clause)
    tuple2ConsequentClauses[consequent].add(clause)

if 'narrowor' in sys.argv:
    logging.info('Narrowing wide disjunctions.')

    wideConsequents = { t for t in allConsequents if len(tuple2ConsequentClauses[t]) >= 10 }

    # Until fixpoint,
    changed = True
    while changed:
        changed = False
        for t in wideConsequents:
            # for each tuple t with too many derivations,
            consequentCount = len(tuple2ConsequentClauses[t])
            if consequentCount < 10: continue
            logging.info('Discovered tuple {0} with {1} proving clauses. Splitting!'.format(t, consequentCount))
            # split!

            t1 = 'D{0}'.format(len(allClauses))
            t2 = 'D{0}'.format(len(allClauses) + 1)
            logging.info('Producing tuples {0} and {1}.'.format(t1, t2))

            # We will make half the proving clauses now prove t1, and the other half prove t2
            # t1 and t2 will each prove t
            # We need to update the following variables in a consistent way:
            # allClauses, allRuleNames, allTuples, allConsequents, tuple2ConsequentClauses, wideConsequents

            c1 = ('NOT ' + t1, t)
            c2 = ('NOT ' + t2, t)

            # allClauses
            allClauses.add(c1)
            allClauses.add(c2)

            # allRuleNames
            allRuleNames[c1] = 'Rnarrow'
            allRuleNames[c2] = 'Rnarrow'

            # allTuples
            allTuples.add(t1)
            allTuples.add(t2)

            # allConsequents
            allConsequents.add(t1)
            allConsequents.add(t2)

            # tuple2ConsequentClauses
            originalProvingClauses = tuple2ConsequentClauses[t]

            tuple2ConsequentClauses[t] = { c1, c2 }
            tuple2ConsequentClauses[t1] = set()
            tuple2ConsequentClauses[t2] = set()

            for originalClause in originalProvingClauses:
                newClause = list(originalClause)
                if len(tuple2ConsequentClauses[t1]) < consequentCount / 2:
                    newClause[-1] = t1
                    newClause = tuple(newClause)
                    tuple2ConsequentClauses[t1].add(newClause)
                else:
                    newClause[-1] = t2
                    newClause = tuple(newClause)
                    tuple2ConsequentClauses[t2].add(newClause)

                allClauses.remove(originalClause)
                allClauses.add(newClause)
                allRuleNames[newClause] = allRuleNames[originalClause]

            assert len(tuple2ConsequentClauses[t1]) < consequentCount
            assert len(tuple2ConsequentClauses[t2]) < consequentCount
            assert len(tuple2ConsequentClauses[t1]) + len(tuple2ConsequentClauses[t2]) == consequentCount

            # wideConsequents
            wideConsequents.remove(t)
            if len(tuple2ConsequentClauses[t1]) >= 10: wideConsequents.add(t1)
            if len(tuple2ConsequentClauses[t2]) >= 10: wideConsequents.add(t2)

            changed = True
            break

########################################################################################################################
# 3. Produce bayesian network

# 3a. Create nodes of the network
allNodes = list(allClauses | allConsequents)
logging.info('Discovered {0} bayesian nodes.'.format(len(allNodes)))

# 3b. Print dictionary file
nodeIndex = {}
with open(dictOutFileName, 'w') as dictOutFile:
    for node in allNodes:
        index = len(nodeIndex)
        nodeIndex[node] = index
        nodeStr = node if node in allTuples else ', '.join(node)
        print('{0}: {1}'.format(index, nodeStr), file=dictOutFile)
    logging.info('Finished producing dictionary.')

# 3c. Output rules for each node
print(len(nodeIndex))
for node in allNodes:
    if node in allClauses:
        assert node not in allConsequents
        clause = node
        parents = set()
        for lit in clause[:-1]:
            t = lit2Tuple(lit)
            if t in nodeIndex:
                parents.add(str(nodeIndex[t]))
        # nodeStr = '* {0} {1} {2} // {3}'.format(allRuleNames[node], len(parents), ' '.join(parents), node)
        nodeStr = '* {0} {1} {2}'.format(allRuleNames[node], len(parents), ' '.join(parents))
        print(nodeStr)
    else:
        assert node in allConsequents
        t = node
        parents = [ str(nodeIndex[clause]) for clause in tuple2ConsequentClauses[node] ]
        # nodeStr = '+ {0} {1} // {2}'.format(len(parents), ' '.join(parents), node)
        nodeStr = '+ {0} {1}'.format(len(parents), ' '.join(parents))
        print(nodeStr)
logging.info('Finished producing Bayesian network.')
