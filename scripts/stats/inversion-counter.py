#!/usr/bin/env python3

# Given a combined.out file containing a ranked list of alarms, and a file name for the output plot, computes various
# statistics about the alarm ranking in combined.out and outputs a chart to the output file.
# ./inversion-counter.py combined.out fraction.pdf

import math
import sys

rankedAlarmsFileName = sys.argv[1]
chartOutputFileName = sys.argv[2]

numTrue = 0
numFalse = 0
numInversions = 0
dcg = 0

index = 0
tpRatios = []
scores = []
ground = []
for line in open(rankedAlarmsFileName):
    if index > 0:
        if line.find('TrueGround') >= 0:
            numTrue = numTrue + 1
            numInversions = numInversions + numFalse
            dcg = dcg + 1.0 / math.log2(index + 1)
            ground.append(1)
        else:
            numFalse = numFalse + 1
            ground.append(-1)

        tpRatios.append(numTrue / (numTrue + numFalse))

        if line.find('PosLabel') >= 0 or \
           line.find('NegLabel') >= 0 or \
           line.find('SPOkGoodGood') >= 0 or \
           line.find('GoodSPOkGood') >= 0:
            scores.append(float(line.split('\t')[1]))
        else:
            scores.append(0)

    index = index + 1

print('Total alarms: {0}'.format(numTrue + numFalse))
print('True alarms: {0}'.format(numTrue))
print('False alarms: {0}'.format(numFalse))
print('Inversion count: {0}'.format(numInversions))
print('Peak inversion count: {0}'.format(numFalse * numTrue))
print('DCG: {0}'.format(dcg))

import matplotlib.pyplot as plt

xindices = list(range(1, len(tpRatios) + 1))
fig, ax1 = plt.subplots()

ax1.plot(xindices, tpRatios, 'b')
ax1.set_xlabel('Alarm rank')
ax1.set_ylabel('Fraction of true positives', color='b')

ax2 = ax1.twinx()
ax2.plot(xindices, scores, 'r')
ax2.set_ylabel('Confidence', color='r')

ax3 = ax1.twinx()
ax3.yaxis.set_visible(False)
ax3.plot(xindices, ground, 'go')
ax3.set_ylabel('Ground truth', color='g')

fig.tight_layout()
plt.savefig(chartOutputFileName, bbox_inches='tight')
