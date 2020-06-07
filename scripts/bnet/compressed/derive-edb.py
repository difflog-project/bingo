#!/usr/bin/env python3

# Given a set of constraints as input on stdin, computes which tuples are EDBs, and adds extra clauses which produce the
# EDBs as consequents. Each EDB relation will be associated with a new rule, and all EDB tuples will be derived as
# consequents of instances of the appropriate rule.

# This is helpful in case one does not want to treat EDB tuples as being inerrant.

# ./scripts/bnet/compressed/derive-edb < named_cons_all.txt.pruned > named_cons_all.txt.edbderived.pruned

import logging
import re
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 1. Accept input

allClauses = set()
allRuleNames = {}

for line in sys.stdin:
    line = line.strip()
    clause = [ literal.strip() for literal in re.split(':|, ', line) ]
    ruleName, clause = clause[0], tuple(clause[1:])

    allRuleNames[clause] = ruleName
    allClauses.add(clause)

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

logging.info('Loaded {0} clauses.'.format(len(allClauses)))
logging.info('Discovered {0} tuples.'.format(len(allTuples)))
logging.info('Discovered {0} consequents.'.format(len(allConsequents)))
logging.info('Discovered {0} input tuples.'.format(len(allInputTuples)))

########################################################################################################################
# 2. Derive EDB clauses

relNameRuleNameMap = {}
for t in allInputTuples:
    if '(' in t:
        relName = t.split('(')[0].strip()
        if relName not in relNameRuleNameMap:
            i = 0
            while 'R{0}'.format(i) in allRuleNames.values(): i = i + 1
            ruleName = 'R{0}'.format(i)
            relNameRuleNameMap[relName] = ruleName
            logging.info('Associating relation {0} with rule {1}.'.format(relName, ruleName))

        ruleName = relNameRuleNameMap[relName]
        allClauses.add((t,))
        allRuleNames[(t,)] = ruleName
    else: logging.info('Leaving tuple {0} underived.'.format(t))

########################################################################################################################
# 3. Print output

for clause in allClauses:
    ruleName = allRuleNames[clause]
    clauseStr = ', '.join(clause)
    print('{0}: {1}'.format(ruleName, clauseStr))

logging.info('Bye!')
