#!/usr/bin/env python3

# Given a set of constraints as input on stdin, computes which tuples are EDBs, and elides them while printing to
# stdout. This rewrite already implicitly happens within bnet2fg.py, and it is helpful to have it explicitly as a
# script.

# ./scripts/bnet/compressed/elide-edb < named_cons_all.txt.pruned > named_cons_all.txt.elided.pruned

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
# 2. Simplify clauses

def simplifyClause(clause):
    return tuple([ lit for lit in clause if lit2Tuple(lit) in allConsequents ])

allSimplifiedClauses = set()
allSimplifiedRuleNames = {}
for clause in allClauses:
    sc = simplifyClause(clause)
    allSimplifiedClauses.add(sc)
    allSimplifiedRuleNames[sc] = allRuleNames[clause]

########################################################################################################################
# 3. Print output

for clause in allSimplifiedClauses:
    ruleName = allSimplifiedRuleNames[clause]
    clauseStr = ', '.join(clause)
    print('{0}: {1}'.format(ruleName, clauseStr))

logging.info('Bye!')
