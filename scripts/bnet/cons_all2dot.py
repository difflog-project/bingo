#!/usr/bin/env python3

# Given a cycle-free set of constraints on stdin, produces a dot representation for display.

# ./cons_all2dot.py ..../oracle_queries.txt ..../base_queries.txt < named_cons_all.txt > named-bnet.dot

# The output of prune-cons will work well as input to this script.

import logging
import re
import sys

oracleQueriesFileName = sys.argv[1]
baseQueriesFileName = sys.argv[2]

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

def lit2PrettyLit(literal):
    return '!'+literal[len('NOT '):] if literal.startswith('NOT ') else literal

def compact(s):
    s1 = s.replace('_cs', '')
    return s1.replace('Hext', '')

########################################################################################################################
# 1. Accept input

allClauses = set()
allTuples = set()
allConsequents = set()
clauseToStr = {}

for line in sys.stdin:
    line = line.strip()
    clause = [ literal.strip() for literal in re.split(':|, ', line) ]
    ruleName = clause[0]
    clause = clause[1:]
    clause = tuple(clause)
    allClauses.add(clause)
    clauseToStr[clause] = ','.join([lit2PrettyLit(literal) for literal in clause])

    for literal in clause:
        allTuples.add(lit2Tuple(literal))

    allConsequents.add(clause2Consequent(clause))

oracleQueries = { line.strip() for line in open(oracleQueriesFileName) }
#assert oracleQueries.issubset(allConsequents)
baseQueries = { line.strip() for line in open(baseQueriesFileName) }
#assert baseQueries.issubset(allConsequents)
assert oracleQueries.issubset(baseQueries)
falseQueries = baseQueries - oracleQueries

allInputTuples = allTuples - allConsequents

logging.info('Loaded {0} clauses.'.format(len(allClauses)))
logging.info('Discovered {0} tuples.'.format(len(allTuples)))
logging.info('Discovered {0} consequents.'.format(len(allConsequents)))
logging.info('Discovered {0} input tuples.'.format(len(allInputTuples)))

########################################################################################################################
# 3. Produce dot representation 

# Map each tuple to the number of clauses deriving it
tuple2ConsequentClauses = { t: set() for t in allTuples }
for clause in allClauses:
    consequent = clause2Consequent(clause)
    tuple2ConsequentClauses[consequent].add(clause)

# 3a. Create nodes of the network
allNodes = list(allClauses | allConsequents)
logging.info('Discovered {0} bayesian nodes.'.format(len(allNodes)))

# 3b. Create dictionary
nodeIndex = {}
for node in allNodes:
    index = len(nodeIndex)
    nodeIndex[node] = index
logging.info('Finished producing dictionary.')

# 3c. Output rules for each node
print("digraph G{")
for node in allNodes:
    if node in allClauses:
        clause = node
        print('    \"{0}\" [shape=box];'.format(compact(clauseToStr[clause])))
    elif node in oracleQueries:
        print('    \"{0}\" [style=filled,color=red];'.format(compact(node)))
    elif node in falseQueries:
        print('    \"{0}\" [style=filled,color=blue];'.format(compact(node)))
    else:
        print('    \"{0}\";'.format(compact(node)))


for node in allNodes:
    if node in allClauses:
        assert node not in allConsequents
        clause = node
        for lit in clause[:-1]:
            t = lit2Tuple(lit)
            if t in allConsequents:
                print('    \"{0}\" -> \"{1}\";'.format(compact(t), compact(clauseToStr[clause])))
    else:
        assert node in allConsequents
        for clause in tuple2ConsequentClauses[node]:
            print('    \"{0}\" -> \"{1}\";'.format(compact(clauseToStr[clause]), compact(node)))
            
print("}")
logging.info('Finished producing dot representation.')
