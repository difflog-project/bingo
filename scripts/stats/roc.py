#!/usr/bin/env python3

# Given a stats.txt file and a file name for the output plot, draws the ROC curve and computes the AUC score. If the
# run was incomplete, but all true alarms were discovered, then an additional parameter TOTAL, the total number of
# alarms in the benchmark, may be specified, and the script will automatically complete the ranking.
# ./auc.py js_500stat.txt auc.pdf [TOTAL]

import logging
import math
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 1. Read arguments

numTrue = int(sys.argv[1])
numFalse = int(sys.argv[2])
outputFileName = sys.argv[3]
primName = sys.argv[4]
primCurveFileName = sys.argv[5]
secNameCurves = sys.argv[6:] if len(sys.argv) > 6 else []

########################################################################################################################
# 2. Load curves

def loadCurve(fname):
    records = [ line.strip() for line in open(fname) if len(line.strip()) > 0 ]
    records = [ line.split('\t') for line in records ]
    records = [ [ c.strip() for c in rec if len(c.strip()) > 0 ] for rec in records ]

    headerLine = records[0]
    records = records[1:]
    groundIndex = headerLine.index('Ground')
    grounds = [ rec[groundIndex] == 'TrueGround' for rec in records ]

    xindices = [ 0 ]
    yindices = [ 0 ]
    for g in grounds:
        if g:
            xindices.append(xindices[-1])
            yindices.append(yindices[-1] + 1)
        else:
            xindices.append(xindices[-1] + 1)
            yindices.append(yindices[-1])

    while yindices[-1] < numTrue:
        xindices.append(xindices[-1])
        yindices.append(yindices[-1] + 1)
    while xindices[-1] < numFalse:
        xindices.append(xindices[-1] + 1)
        yindices.append(yindices[-1])

    return (xindices, yindices)

primCurve = loadCurve(primCurveFileName)
secNameCurves = [ { 'name': secNameCurves[i], \
                    'fname' : secNameCurves[i + 1], \
                    'curve': loadCurve(secNameCurves[i + 1]) } for i in range(0, len(secNameCurves), 2) ]

########################################################################################################################
# 3. Plot curve!

def doplot(curveName, curve, isPrimary=False):
    xindices, yindices = curve
    ans = plt.plot(xindices, yindices, label=curveName, linewidth=2) if isPrimary else \
          plt.plot(xindices, yindices, label=curveName, linestyle='-.', linewidth=1)

    ans = ans[0]
    return ans

primLine = doplot(primName, primCurve, isPrimary=True)
secLines = [ doplot(snc['name'], snc['curve'], isPrimary=False) for snc in secNameCurves ]
allLines = [ primLine ] + secLines
allLabels = [ line.get_label() for line in allLines ]

plt.plot([0, numFalse / 2, numFalse],[0, numTrue / 2, numTrue], ':')

ax = plt.axes()
ax.set_xlabel('Number of false alarms inspected', fontsize=14)
ax.set_xbound(lower=0, upper=numFalse)
ax.set_ylabel('Number of true alarms inspected', fontsize=14)
ax.tick_params(labelsize=12)
plt.ylim(ymin=0, ymax=numTrue)

legend = ax.legend(allLines, allLabels[0:2], fontsize=14)

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
plt.savefig(outputFileName, bbox_inches='tight')
