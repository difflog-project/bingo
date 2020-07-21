#!/usr/bin/env pypy3

########################################################################################################################
# Usage: ./elim-inconsistent-feedback.py named_cons_all.txt feedback.txt skipTuples.txt

# Input:
# 1. named_cons_all.txt:
# 2. feedback.txt: "O t true" or "O t false", for a set of tuples t, in the same format accepted by driver.py
#    NOTE 1: No AC or MAC command at the end of the file
#    NOTE 2: No confidence values enter this file. They are handled separately, in observed-queries.txt
# 3. nonSkipTuples.txt:

# Output: Produces a new set of feedback commands, printed to stdout
# Guarantee: feedback-out subseteq feedback-in

########################################################################################################################
# 0. Preamble

from collections import namedtuple
import logging
import re
import sys

consAllFilename, feedbackFilename, skipTuplesFilename = sys.argv[1:]

logging.basicConfig(level=logging.INFO, \
                    format='[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s', \
                    datefmt='%H:%M:%S')

logging.info('Hello!')
logging.info(f'Running elim-inconsistent-feedback.py {consAllFilename} {feedbackFilename} {skipTuplesFilename}')

########################################################################################################################
# 1. Read Clauses

Clause = namedtuple('Clause', [ 'ruleName', 'head', 'body' ])
def parseClause(line):
    line = line.strip()
    line = [ literal.strip() for literal in re.split(':|, ', line) ]

    ruleName = line[0]
    literals = line[1:]

    assert len(literals) >= 1
    if not all(literal.startswith('NOT ') for literal in literals[:-1]): print(line)
    assert all(literal.startswith('NOT ') for literal in literals[:-1])
    assert not literals[-1].startswith('NOT ')

    def lit2Tuple(literal): return literal if not literal.startswith('NOT ') else literal[len('NOT '):]
    literals = [ lit2Tuple(literal) for literal in literals ]
    head = literals[-1]
    body = tuple(literals[:-1])

    return Clause(ruleName, head, body)

allClauses = [ line.strip() for line in open(consAllFilename) ]
allClauses = [ line for line in allClauses if line ]
allClauses = [ parseClause(line) for line in allClauses ]

allTuples = { clause.head for clause in allClauses } | { t for clause in allClauses for t in clause.body }
allConsequents = { clause.head for clause in allClauses }

logging.info(f'Read {len(allClauses)} clauses')
logging.info(f'{len(allTuples)} tuples discovered')
logging.info(f'{len(allConsequents)} IDB tuples discovered')

########################################################################################################################
# 2. Read Feedback

origFeedback = [ line.strip() for line in open(feedbackFilename) ]
assert all(line.startswith('O ') for line in origFeedback)
origFeedback = [ line.split(' ') for line in origFeedback ]
origFeedback = { line[1].strip(): line[2].strip() for line in origFeedback }
assert all(v == 'true' or v == 'false' for t, v in origFeedback.items())
origFeedback = { t: (v == 'true') for t, v in origFeedback.items() }
assert all(t in allTuples for t in origFeedback)

logging.info(f'Read {len(origFeedback)} feedback tuples')

########################################################################################################################
# 3. Make Feedback Consistent

# Rule 0:
# For all t in feedback, confirm t is not skip
# TODO: Not yet implemented!

# Rule 1:
# If we have a clause c = "a1, a2, ..., ak => t" and feedback[ai] = false,
# then feedback[c] = false
# NOTE: Each clause is basically shorthand for (a1 and a2 and ... ak) => t

# Rule 2:
# If we have a tuple t, derived by clauses:
# c1: b1 => t,
# c2: b2 => t,
# ...
# ck: bk => t,
# and feedback[ci] = false for all ci,
# then feedback[t] = false
# NOTE: Each set of such clauses is basically shorthand for (b1 or b2 or ... or bk) => t

# Finally, feedback := newFeedback intersection origFeedback

# Informally, we are "pushing false forwards"
# Why don't we "push true backwards"?
# Because we know how to push false forwards, but pushing true backwards is tricky

####
# 3a. Compute l1Upstream and l1Downstream

# l1Upstream[t] = all clauses of which t is head
# l1Downstream[t] = all clauses in which t appears

l1Upstream = { t: set() for t in allTuples }
l1Downstream = { t: set() for t in allTuples }
for clause in allClauses:
    l1Upstream[clause.head] |= { clause }
    for t in clause.body:
        l1Downstream[t] |= { clause }

logging.info('Computed l1Upstream and l1Downstream')

####
# 3b. Fixpoint loop!

logging.info('Beginning fixpoint loop')

falseClauses = set()
newFeedback = dict(origFeedback)

tupleQueue = { t for t, v in origFeedback.items() if not v }
while tupleQueue:
    # logging.info(f'len(tupleQueue): {len(tupleQueue)}')
    t = tupleQueue.pop()
    assert not newFeedback[t]
    for clause in l1Downstream[t]:
        if clause not in falseClauses:
            falseClauses |= { clause }
            tPrime = clause.head
            if l1Upstream[tPrime].issubset(falseClauses):
                if tPrime not in newFeedback or newFeedback[tPrime]:
                    newFeedback[tPrime] = False
                    tupleQueue |= { tPrime }

feedback = { t: v for t, v in origFeedback.items() if newFeedback[t] == v }
logging.info(f'Derived {len(feedback)} final feedback tuples')

########################################################################################################################
# 4. Print Output

for t, v in feedback.items():
    print(f'O {t} {str(v).lower()}')

logging.info('Bye!')
