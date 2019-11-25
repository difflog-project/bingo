#!/usr/bin/env python3

import sys

prefixFilter = sys.argv[1]
fnames = sys.argv[2:]

def readlines(fname):
    return [ line.strip() for line in open(fname) if line.strip().startswith(prefixFilter) ]

ftuples = { fname: set(readlines(fname)) for fname in fnames }
allTuples = set()
for fname in fnames:
    allTuples = allTuples | ftuples[fname]

print('Tuple\t{0}'.format('\t'.join(fnames)))
for t in allTuples:
    print('{0}\t{1}'.format(t, '\t'.join([ str(t in fname) for fname in fnames ])))
