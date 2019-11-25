#!/usr/bin/env python3

# Intended to be run from the chord-fork folder. Given base_queries.txt and oracle_queries.txt, produces a labelled set
# alarms on stdout.

# cd Error-Ranking/chord-fork
# ./scripts/label-alarms.py oracle_queries.txt < base_queries.txt > labelled_queries.txt

# The output is in a format similar to the following:
# racePairs_cs(12,34) true
# racePairs_cs(32,29) false
# racePairs_cs(19,12) false
# racePairs_cs(19,19) true

import sys

oracleQueriesFileName = sys.argv[1]

oracleQueries = set([ line.strip() for line in open(oracleQueriesFileName) if len(line.strip()) > 0 ])

for t in sys.stdin:
    t = t.strip()
    if len(t) == 0: continue
    print('{0} {1}'.format(t, 'true' if t in oracleQueries else 'false'))
