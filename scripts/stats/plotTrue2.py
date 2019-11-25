#!/usr/bin/env python3

# Given a js_Xstat.txt file and a file name for the output plot,
# draw the ROC curve and computes the AUC score.
# ./auc.py js_500stat.txt auc.pdf

import math
import sys

rankedAlarmsFileName = sys.argv[1]
chartOutputFileName = sys.argv[2]
name = sys.argv[3]
total = sys.argv[4]

numTrue = 0
numFalse = 0

index = 0
tpRatios = []
scores = []
xindices = [0]
yindices = [0]
xindicesIdeal = [0]
yindicesIdeal = [0]
for line in open(rankedAlarmsFileName):
    if index > 0:
        if line.find('TrueGround') >= 0:
            numTrue = numTrue + 1
        else:
            numFalse = numFalse + 1
        yindices.append(numTrue)
        xindices.append(index)
    index = index + 1

print('#Iterations: {0}'.format(numTrue + numFalse))
print('True alarms: {0}'.format(numTrue))
print('False alarms: {0}'.format(numFalse))

index = 1
while True:
    if index <= numTrue:
        xindicesIdeal.append(index)
        yindicesIdeal.append(index)
    elif index <= int(total):
        xindicesIdeal.append(index)
        yindicesIdeal.append(numTrue)
    else:
        break
    index = index + 1

# plot
import matplotlib.pyplot as plt
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0
t = name + ' (total = ' + str(total) + ')'
plt.title(t)

plt.plot(xindices, yindices, 'b')
plt.plot(xindicesIdeal, yindicesIdeal, 'r--')
plt.xlabel('#Iterations')
plt.ylabel('#Bugs')


plt.savefig(chartOutputFileName + "1.pdf", bbox_inches='tight')
plt.ylim([0,int(total)])
plt.savefig(chartOutputFileName + "2.pdf", bbox_inches='tight')
