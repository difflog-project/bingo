#!/usr/bin/env python3

# Command-line arguments:
#    list of tuples whose ancestry is required
#    a set of clauses as input on stdin
# Output:
#    set of ancestor clauses on stdout.
#
# Example invocation:
# ./anc.py racePairs_cs(123,129) racePairs_cs(982,123) racePairs_cs(214,124) < cons_all.txt.pruned > anc.txt

import logging
import re
import sys

ancestorTuples = sys.argv[1:]
ancestorTuples = { t.strip() for t in ancestorTuples }

nolevel = 'nolevel' in ancestorTuples
if nolevel: ancestorTuples.remove('nolevel')

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
# 2. Compute the ancestor tuples
# The ancestry of a set of tuples are all the clauses that were (transitively) involved in deriving those tuples

numChanged = float('inf')
while numChanged > 0:
    numChanged = 0
    for clause in allClauses:
        consequent = clause2Consequent(clause)
        if consequent in ancestorTuples:
            for literal in clause[:-1]:
                t = lit2Tuple(literal)
                if t not in ancestorTuples:
                    numChanged = numChanged + 1
                    ancestorTuples.add(t)

ancestorTuples = ancestorTuples - allInputTuples
logging.info('Discovered {0} IDB ancestor tuples in all.'.format(len(ancestorTuples)))

########################################################################################################################
# 3. Compute the ancestor clauses and produce output

derivedTuples = set()
derivedTuples |= allInputTuples
ancLevel = {}

level = 0
addedClauses = set()
while len(ancestorTuples - derivedTuples) > 0:
   newDerivedTuples = set()
   clausesToProcess = allClauses - addedClauses
   for clause in clausesToProcess:
      consequent = clause2Consequent(clause)
      antecedents = clause2Antecedents(clause)
      if (consequent in ancestorTuples) and ((set(antecedents)).issubset(derivedTuples)):
         if level not in ancLevel:
            ancLevel[level] = set()
         ancLevel[level].add(clause) 
         addedClauses.add(clause)
         newDerivedTuples.add(consequent)
   assert len(newDerivedTuples) > 0
   derivedTuples |= newDerivedTuples
   level += 1


numClauses = 0
for level, levelClauses in ancLevel.items():
   #logging.info('Discovered {0} ancestor clauses at level {1}.'.format(len(levelClauses), level))
   numClauses += len(levelClauses)
   if level > 0:
      for clause in sorted(levelClauses):
         ruleName = allRuleNames[clause]
         clauseStr = ', '.join(clause)
         if nolevel: print('{0}: {1}'.format(ruleName, clauseStr))
         else: print('{0}: {1}: {2}'.format(level, ruleName, clauseStr))

logging.info('Discovered {0} ancestor clauses in all.'.format(numClauses))
