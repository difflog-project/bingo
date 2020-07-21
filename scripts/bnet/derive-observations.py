#!/usr/bin/env python3

# Given:
# 1. fixpoint constraints (i.e., named_cons_all.txt),
# 2. list of observed tuples with their associated observation confidences, and
# 3. list of current rule probabilities (i.e., rule-prob.txt),
# produces a new named_cons_all.txt file with the observed nodes explicitly derived, and produces a new rule probability
# file.

# File containing observed tuples (i.e., observed-queries.txt) formatted as tab-separated values:
# t1	confidence1
# t2	confidence2
# ...

# ./scripts/bnet/compressed/derive-observations.py named_cons_all.txt \
#                                                  observed-queries.txt \
#                                                  rule-prob.txt \
#                                                  named_cons_all.txt.obs-derived \
#                                                  rule-prob.txt.obs-derived

# For each observed tuple t, simply introduces a new derived tuple Obst and a clause
# RObst: NOT t, Obst
# And associates the rule RObst with the corresponding observation confidence.

########################################################################################################################

import logging
import re
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

namedConsAllFilename, observedQueriesFilename, ruleProbFilename, \
outNamedConsAllFilename, outRuleProbFilename = sys.argv[1:]

########################################################################################################################
# 1. Accept input

allClauses = set()
allRuleNames = {}

####
# 1a. Read clauses

for line in open(namedConsAllFilename):
    line = line.strip()
    clause = [ literal.strip() for literal in re.split(':|, ', line) ]
    ruleName, clause = clause[0], tuple(clause[1:])

    allRuleNames[clause] = ruleName
    allClauses.add(clause)

####
# 1b. Read tuples to observe

allObservedTuples = [ line.strip() for line in open(observedQueriesFilename) ]
allObservedTuples = [ line.split('\t') for line in allObservedTuples ]
allObservedTuples = { (t.strip(), float(p)) for t, p in allObservedTuples }

####
# 1c. Load rule probabilities

ruleProbs = [ line.strip().split(': ') for line in open(ruleProbFilename) ]
ruleProbs = { line[0]: float(line[1]) for line in ruleProbs }

####
# 1d. Miscellaneous functions

def lit2Tuple(literal):
    return literal if not literal.startswith('NOT ') else literal[len('NOT '):]

def clause2Antecedents(clause):
    return [ lit2Tuple(literal) for literal in clause[:-1] ]

def clause2Consequent(clause):
    consequent = clause[-1]
    assert not consequent.startswith('NOT ')
    return consequent

allTuples = { lit2Tuple(literal) for clause in allClauses for literal in clause }
allConsequents = { clause2Consequent(clause) for clause in allClauses }
allInputTuples = allTuples - allConsequents

####
# 1e. Acknowledge inputs

for t, p in allObservedTuples:
    assert t in allTuples, f'Unable to locate observed tuple {t}.'
    assert 0.0 <= p and p <= 1.0, f'Ill-formed observation confidence {p} for tuple {t}'

logging.info(f'Loaded {len(allClauses)} clauses.')
logging.info(f'Discovered {len(allTuples)} tuples.')
logging.info(f'Observing {len(allObservedTuples)} tuples.')
logging.info(f'Loaded {len(ruleProbs)} rule probabilities.')

########################################################################################################################
# 2. Produce observation tuples

index = 0
for t, p in allObservedTuples:
    newT = 'Obs' + t

    newRuleName = None
    while newRuleName is None:
        candidateRuleName = f'RObs{index}'
        index = index + 1
        if candidateRuleName not in ruleProbs:
            newRuleName = candidateRuleName
    newClause = (f'NOT {t}', newT)

    allClauses |= { newClause }
    allRuleNames[newClause] = newRuleName
    ruleProbs[newRuleName] = p

    assert newT not in allTuples
    assert newT not in allConsequents
    allTuples |= { newT }
    allConsequents |= { newT }

########################################################################################################################
# 3. Print output

####
# 3a. New list of clauses

with open(outNamedConsAllFilename, 'w') as outNamedConsAllFile:
    for clause in allClauses:
        ruleName = allRuleNames[clause]
        clauseStr = ', '.join(clause)
        print(f'{ruleName}: {clauseStr}', file=outNamedConsAllFile)

####
# 3b. New rule probability file

with open(outRuleProbFilename, 'w') as outRuleProbFile:
    for r, p in ruleProbs.items():
        print(f'{r}: {p}', file=outRuleProbFile)

logging.info('Bye!')
