#!/usr/bin/env python3

# Given a stats.txt file and a file name for the output plot, draws the ROC curve and computes the AUC score. If the
# run was incomplete, but all true alarms were discovered, then an additional parameter TOTAL, the total number of
# alarms in the benchmark, may be specified, and the script will automatically complete the ranking.
# ./auc.py js_500stat.txt auc.pdf [TOTAL]

import math
import sys

rankedAlarmsFileName = sys.argv[1]
chartOutputFileName = sys.argv[2]
totalAlarm = sys.argv[3] if len(sys.argv) >= 4 else None

numTrue = 0
numFalse = 0

index = 0
tpRatios = []
scores = []
xindices = [0]
yindices = [0]
for line in open(rankedAlarmsFileName):
    if index > 0:
        if line.find('TrueGround') >= 0:
            numTrue = numTrue + 1
        else:
            numFalse = numFalse + 1
        xindices.append(numFalse)
        yindices.append(numTrue)
    index = index + 1

if totalAlarm != None:
    while index <= int(totalAlarm):
        numFalse = numFalse + 1
        xindices.append(numFalse)
        yindices.append(numTrue)
        index = index + 1

print('Total alarms: {0}'.format(numTrue + numFalse))
print('True alarms: {0}'.format(numTrue))
print('False alarms: {0}'.format(numFalse))

xindices = list(map(lambda x: float(x) / float(numFalse), xindices))
yindices = list(map(lambda x: float(x) / float(numTrue), yindices))

# auc
x0 = 0.0
auc = 0.0
for (x,y) in zip(xindices, yindices):
    auc = auc + (x - x0) * y
    x0 = x

print('AUC: {0}'.format(auc))

# plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0

fig, ax1 = plt.subplots()
ax1.plot(xindices, yindices, 'b')
ax1.set_xlabel('False Positive Ratio')
ax1.set_ylabel('True Positive Ratio')

ax1.plot([0,0.5,1],[0,0.5,1],'r--')

fig.tight_layout()
plt.savefig(chartOutputFileName, bbox_inches='tight')
