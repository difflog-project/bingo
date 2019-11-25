#!/usr/bin/env python3

# Given a list of base queries, a list of oracle queries, and a noise fraction p, where 0 <= p <= 1, adds the required
# amount of noise to the oracle and prints it to stdout. In particular, for each alarm a, with probability (1-p), the
# ground truth is preserved, i.e. it is output iff it is present in the original oracle, and with probability p, its
# ground truth is set to random noise. The random noise is true with the same probability as the fraction of true
# positives in the real ground truth, and so the number of alarms output is roughly equal to the number of alarms in the
# original oracle_queries.txt.

# ./scripts/add-noise.py base_queries.txt oracle_queries.txt 0.05 > noisy_oracle_queries.txt

import logging
import random
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

baseQueriesFileName, oracleQueriesFileName, flipProb = sys.argv[1:]
flipProb = float(flipProb)
assert 0 <= flipProb and flipProb <= 1

########################################################################################################################
# 1. Load oracle and base queries

baseQueries = { line.strip() for line in open(baseQueriesFileName) if len(line.strip()) > 0 }
oracleQueries = { line.strip() for line in open(oracleQueriesFileName) if len(line.strip()) > 0 }
assert oracleQueries.issubset(baseQueries)

########################################################################################################################
# 2. Add noise

for t in baseQueries:
    realTruth = t in oracleQueries
    noise = random.uniform(0, 1) < len(oracleQueries) / len(baseQueries)
    noisyTruth = realTruth if random.uniform(0, 1) > flipProb else noise
    if noisyTruth: print(t)
