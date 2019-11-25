#!/usr/bin/env python3

import math
import sys

rankedAlarmsFileName = sys.argv[1]
chartOutputFileName = sys.argv[2]
iteration = sys.argv[3]
name = sys.argv[4]
total = sys.argv[5]

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
    if index > int(iteration):
        break
    if index > 0:
        if line.find('TrueGround') >= 0:
            numTrue = numTrue + 1
        else:
            numFalse = numFalse + 1
        yindices.append(numTrue)
        xindices.append(index)
    index = index + 1

index = 1
while index <= numTrue:
    yindicesIdeal.append(index)
    xindicesIdeal.append(index)
    index = index + 1

print('#Iterations: {0}'.format(numTrue + numFalse))
print('True alarms: {0}'.format(numTrue))
print('False alarms: {0}'.format(numFalse))

# plot
import matplotlib.pyplot as plt
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0
t = name + ' (total = ' + total + ')'
plt.title(t)

plt.plot(xindices, yindices, 'b')
plt.plot(xindicesIdeal, yindicesIdeal, 'r--')
plt.xlabel('#Iterations')
plt.ylabel('#Bugs')

plt.savefig(chartOutputFileName, bbox_inches='tight')
