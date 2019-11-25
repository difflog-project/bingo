#!/usr/bin/env python3

# Given a set of cycle-free constraints, a rule probabilities file, the default rule probability, and a set of base
# queries, eliminates those tuples which can be derived in only one way, and which are used in the derivation of only
# one other tuple, and which are not present in the base queries list. The last two arguments specify the output files:
# new-rule-prob.txt is the new rule probabilities file to be used by subsequent components of the system, and
# named_cons_all.txt.cep is the new file containing grounded constraints.

# ./scripts/bnet/compressed/compress-cons-all.py \
# named_cons_all.txt.elided.pruned \
# rule-prob.txt \
# 0.999 \
# base_queries.txt \
# new-rule-prob.txt \
# named_cons_all.txt.cep

import logging
import random
import re
import sys

consAllFileName, ruleProbFileName, defaultRuleProb, baseQueriesFileName, \
newRuleProbFileName, outputConsAllFileName = sys.argv[1:]

defaultRuleProb = float(defaultRuleProb)
assert 0 <= defaultRuleProb and defaultRuleProb <= 1

random.seed(0)
logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")
logging.info('Hello!')

########################################################################################################################
# 1. Accept input

# Load grounded constraints
allClauses = set()
allRuleNames = {}

for line in open(consAllFileName):
    line = line.strip()
    clause = [ literal.strip() for literal in re.split(':|, ', line) ]
    ruleName, clause = clause[0], tuple(clause[1:])

    allRuleNames[clause] = ruleName
    allClauses.add(clause)

# Load rule probabilities
ruleProbs = [ line.strip().split(': ') for line in open(ruleProbFileName) ]
ruleProbs = { line[0]: float(line[1]) for line in ruleProbs }
for clause in allClauses:
    ruleName = allRuleNames[clause]
    if ruleName not in ruleProbs: ruleProbs[ruleName] = defaultRuleProb

def makeNewRule(ruleProb):
    ruleIndex = random.randint(0, 10 * len(ruleProbs))
    while 'R{0}'.format(ruleIndex) in ruleProbs: ruleIndex = random.randint(0, 10 * len(ruleProbs))
    ruleName = 'R{0}'.format(ruleIndex)
    ruleProbs[ruleName] = ruleProb
    return ruleName

# Load base queries
baseQueries = { line.strip() for line in open(baseQueriesFileName) if len(line.strip()) > 0 }

########################################################################################################################
# 2. Definitions

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
assert len(allInputTuples) == 0

logging.info('Loaded {0} clauses.'.format(len(allClauses)))
logging.info('Discovered {0} tuples.'.format(len(allTuples)))
logging.info('Discovered {0} consequents.'.format(len(allConsequents)))
logging.info('Discovered {0} input tuples.'.format(len(allInputTuples)))

########################################################################################################################
# 3. Compute source and sink clauses of each tuple
# A source clause of a tuple t is a clause with t as its consequent.
# A sink clause of a tuple t is a clause with t as one of its antecedents.

sourceClauses = { t: set() for t in allTuples }
sinkClauses = { t: set() for t in allTuples }
for clause in allClauses:
    consequent = clause2Consequent(clause)
    sourceClauses[consequent].add(clause)
    for t in clause2Antecedents(clause): sinkClauses[t].add(clause)

eliminableTuples = { t for t in allTuples if len(sourceClauses[t]) == 1 \
                                         and len(sinkClauses[t]) == 1 \
                                         and t not in baseQueries }

logging.info('Discovered {0} eliminable tuples.'.format(len(eliminableTuples)))

########################################################################################################################
# 4. Eliminate tuples

while len(eliminableTuples) > 0:
    t = eliminableTuples.pop()
    srcClause = sourceClauses[t].pop()
    sinkClause = sinkClauses[t].pop()

    newClause = list(srcClause[:-1] + sinkClause)
    newClause = [ lit for lit in newClause if not lit == 'NOT {0}'.format(t) ]
    newClause = tuple(newClause)

    srcProb = ruleProbs[allRuleNames[srcClause]]
    sinkProb = ruleProbs[allRuleNames[sinkClause]]
    newClauseProb = srcProb * sinkProb
    newRuleName = makeNewRule(newClauseProb)

    logging.info('')
    logging.info('Eliminating tuple {0}.'.format(t))
    logging.info('Source clause: {0}. Probability: {1}.'.format(', '.join(srcClause), srcProb))
    logging.info('Sink clause: {0}. Probability: {1}.'.format(', '.join(sinkClause), sinkProb))
    logging.info('New clause: {0}. Probability: {1}.'.format(', '.join(newClause), newClauseProb))
    logging.info('Introducing new rule: {0}.'.format(newRuleName))

    allClauses.remove(srcClause)
    allClauses.remove(sinkClause)
    allClauses.add(newClause)
    logging.info('len(allClauses): {0}'.format(len(allClauses)))

    allRuleNames[newClause] = newRuleName

    allTuples.remove(t)
    allConsequents.remove(t)
    if t in allInputTuples: allInputTuples.remove(t)

    del sourceClauses[t]
    finalConsequent = clause2Consequent(newClause)
    sourceClauses[finalConsequent].remove(sinkClause)
    sourceClauses[finalConsequent].add(newClause)

    del sinkClauses[t]
    for tp in set(clause2Antecedents(srcClause)):
        assert not tp == t
        logging.info('Removing srcClause={0} from sinkClauses[tp={1}].'.format(', '.join(srcClause), tp))
        sinkClauses[tp].remove(srcClause)
        sinkClauses[tp].add(newClause)
    for tp in set(clause2Antecedents(sinkClause)):
        if tp == t: continue
        logging.info('Removing sinkClause={0} from sinkClauses[tp={1}].'.format(', '.join(sinkClause), tp))
        sinkClauses[tp].remove(sinkClause)
        sinkClauses[tp].add(newClause)

    assert newClause in sourceClauses[finalConsequent]
    for tp in clause2Antecedents(newClause):
        assert newClause in sinkClauses[tp], \
               'Unable to find newClause={0} in sinkClauses[tp={1}].'.format(', '.join(newClause), tp)

logging.info('Maximum new clause length: {0}.'.format(max([ len(clause) for clause in allClauses ])))

########################################################################################################################
# 3. Print output

with open(newRuleProbFileName, 'w') as newRuleProbFile:
    for ruleName, ruleProb in ruleProbs.items():
        print('{0}: {1}'.format(ruleName, ruleProb), file=newRuleProbFile)

with open(outputConsAllFileName, 'w') as outputConsAllFile:
    for clause in allClauses:
        print('{0}: {1}'.format(allRuleNames[clause], ', '.join(clause)), file=outputConsAllFile)

logging.info('Bye!')
