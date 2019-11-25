#!/usr/bin/env python3

# Given a set of tuples as a command-line argument, and given a set of cycle-free clauses as input on stdin, produces
# the set of all ancestors and descendants.
# Both the formats of cons_all.txt and named_cons_all.txt will work as input. For example:
# ./anc-desc.py label(42,18) label(92,32) < named_cons_all.txt.pruned

import logging
import re
import sys

rootTuples = set(sys.argv[1:])

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
# 2. Compute ancestors and descendants
# The ancestors of a clause includes its antecedents.
# The descendants of a clause includes its consequent.

antecedentMap = { t: set() for t in allTuples }
for clause in allClauses:
    for t in clause2Antecedents(clause): antecedentMap[t].add(clause)

consequentMap = { t: set() for t in allTuples }
for clause in allClauses: consequentMap[clause2Consequent(clause)].add(clause)

def ancestors(rootClauses):
    processedAncestors = set()
    unprocessedAncestors = { antecedent for clause in rootClauses for antecedent in clause2Antecedents(clause) }

    while len(unprocessedAncestors) > 0:
        t = unprocessedAncestors.pop()
        processedAncestors.add(t)

        for clause in consequentMap[t]:
            for antecedent in clause2Antecedents(clause):
                if (antecedent not in processedAncestors) and (antecedent not in unprocessedAncestors):
                    unprocessedAncestors.add(antecedent)

    return processedAncestors

def descendants(rootClauses):
    processedDescendants = set()
    unprocessedDescendants = { clause2Consequent(clause) for clause in rootClauses }

    while len(unprocessedDescendants) > 0:
        t = unprocessedDescendants.pop()
        processedDescendants.add(t)

        for clause in antecedentMap[t]:
            consequent = clause2Consequent(clause)
            if (consequent not in processedDescendants) and (consequent not in unprocessedDescendants):
                unprocessedDescendants.add(consequent)

    return processedDescendants

########################################################################################################################
# 3. Produce output

rootClauses = { clause for clause in allClauses if clause2Consequent(clause) in rootTuples }

print('Ancestors:')
for t in ancestors(rootClauses): print(t)

print()

print('Descendants:')
for t in descendants(rootClauses): print(t)
