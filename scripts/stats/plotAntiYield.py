#!/usr/bin/env python3

# Plots anti-yield statistics from the interaction model, i.e the alarm carousel.
# The anti-yield curve is the fraction of false alarms examined, as a function of the number of inspected alarms.
# Takes as input the stats.txt file from a primary AC run (for e.g., from the Bayesian ranker), and the stats.txt files
# from a set of secondary AC runs (for e.g., from the MLN rankers), and plots the anti-yield curves.

# ./scripts/stats/plotAntiYield.py "Bayesian ranker" stats.txt \
#                                  "MLN ranker, iteration 1" base-stats-1.txt \
#                                  "MLN ranker, iteration 2" base-stats-2.txt \
#                                  ... \
#                                  "MLN ranker, iteration n" base-stats-n.txt \
#                                  output.pdf

import math
import matplotlib.pyplot as plt
import sys

inputNames = sys.argv[1:-1]
outputFileName = sys.argv[-1]

print(inputNames)
assert len(inputNames) > 0
assert len(inputNames) % 2 == 0
inputs = [ (inputNames[i], inputNames[i + 1]) for i in range(0, len(inputNames), 2) ]

numTrue = None
numFalse = None

def doplot(inpt, isPrimary=False):
    curveName, statsFileName = inpt

    headerLine = []
    records = []
    with open(statsFileName) as statsFile:
        records = [ line.strip() for line in statsFile ]
        records = [ line.split('\t') for line in records if len(line) > 0 ]
        headerLine = records[0]
        records = records[1:]

    fracFalse = [ 1 - float(rec[headerLine.index('Fraction')]) for rec in records ]
    ntrue = [ int(rec[headerLine.index('NumTrue')]) for rec in records ]
    nfalse = [ int(rec[headerLine.index('NumFalse')]) for rec in records ]

    global numTrue
    global numFalse
    assert numTrue is None or numTrue == ntrue[-1]
    assert numFalse is None or numFalse == nfalse[-1]
    numTrue = ntrue[-1]
    numFalse = nfalse[-1]
    assert numTrue > 0

    print('For {0}, anti-yield at full-rank is {1}.'.format(curveName, fracFalse[numTrue - 1]))

    xindices = list(range(1, len(records) + 1))
    ans = plt.plot(xindices, fracFalse, label=curveName, linewidth=2) if isPrimary else \
          plt.plot(xindices, fracFalse, label=curveName, linestyle='dashed', linewidth=1)

    ans = ans[0]
    return ans

primaryLine = doplot(inputs[0], isPrimary=True)
secondaryLines = [ doplot(inputs[i]) for i in range(1, len(inputs)) ]
allLines = [ primaryLine ] + secondaryLines
allLabels = [ line.get_label() for line in allLines ]

ax = plt.axes()
ax.set_xlabel('Number of alarms inspected')
ax.set_xbound(lower=0, upper=numTrue + numFalse)
ax.set_ylabel('Fraction of false alarms')
plt.ylim(ymin=0, ymax=1)

plt.text(numTrue, 1, '{0} true alarms'.format(numTrue), rotation=90, ha='right', va='top')
plt.axvline(numTrue, color='k', linewidth=1)
legend = ax.legend(allLines, allLabels)

plt.savefig(outputFileName, bbox_inches='tight')
