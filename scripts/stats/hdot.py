#!/usr/bin/env python3

# Given a directory containing the combined files produced by the driver.py AC command, 0.out, 1.out, 2.out, ..., plots
# the scatter plot of the distribution of true alarms.

# Arguments:
# 1. stats.txt file produced by driver.py
# 2. Directory containing the combined files produced by the driver.py AC command, 0.out, 1.out, 2.out, ...
# 3. Name of the output file.
# 4. 'finish'. Optional argument. In case the driver.py AC run is still incomplete, but all true positives have already
#    been produced, then completes the run.

# ./scripts/stats/hdot.py ~/Scratch/stats.txt ~/Scratch/acombined output.pdf [finish]

from enum import Enum
import math
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import logging
import numpy
import os
import os.path
import sys

statsFileName = sys.argv[1]
combinedDirName = sys.argv[2]
outputFileName = sys.argv[3]
finishPlot = 'finish' in sys.argv[4:]

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 1. Read combined files

combinedFiles = [ fname for fname in os.listdir(combinedDirName) ]
combinedFiles = [ fname for fname in combinedFiles if os.path.isfile(os.path.join(combinedDirName, fname)) ]
combinedFiles = [ int(fname[:-4]) for fname in combinedFiles if fname.endswith('.out') ]
combinedFiles = sorted(combinedFiles)
combinedFiles = [ '{0}.out'.format(findex) for findex in combinedFiles ]
logging.info('List of combined files: {0}'.format(combinedFiles))
combinedFiles = [ os.path.join(combinedDirName, fname) for fname in combinedFiles ]
assert len(combinedFiles) > 0

Status = Enum('Status', 'LabTrue UnlabTrue UnlabFalse LabFalse')
PixVal = { Status.LabTrue: 3, Status.UnlabTrue: 1, Status.UnlabFalse: -1, Status.LabFalse: -3 }

def getvec(fname):
    records = [ line.strip() for line in open(fname) ]
    records = [ line.split('\t') for line in records if len(line) > 0 ]

    headerLine = records[0]
    records = records[1:]
    assert len(records) > 0

    groundIndex = headerLine.index('Ground')
    labelIndex = headerLine.index('Label')

    ansDict = { ('TrueGround', 'PosLabel'): Status.LabTrue, \
                ('TrueGround', 'Unlabelled'): Status.UnlabTrue, \
                ('FalseGround', 'Unlabelled'): Status.UnlabFalse, \
                ('FalseGround', 'NegLabel'): Status.LabFalse }

    ans = [ ansDict[(rec[groundIndex], rec[labelIndex])] for rec in records ]
    return ans

def finishPlot(hmap):
    lastCol = hmap[-1]
    assert Status.UnlabTrue not in lastCol, 'There still exists an undiscovered true alarm! Bad! Bad! Bad!'

    while Status.UnlabFalse in lastCol:
        lastCol = list(lastCol)
        for index in reversed(range(len(lastCol))):
            if lastCol[index] == Status.UnlabFalse:
                lastCol[index] = Status.LabFalse
                break
        hmap.append(lastCol)

    return hmap

hmap = [ getvec(fname) for fname in combinedFiles ]
if finishPlot: hmap = finishPlot(hmap)
for col in hmap: assert len(col) == len(hmap[0])

numIters = len(hmap)
numAlarms = len(hmap[0])
numTrue = len([ v for v in hmap[0] if v == Status.LabTrue or v == Status.UnlabTrue ])
numFalse = numAlarms - numTrue

logging.info(numIters)
logging.info(numAlarms)
logging.info(numTrue)
logging.info(numFalse)

########################################################################################################################
# 2. Read stats file

statsHeaderLine = []
statsRecords = []
with open(statsFileName) as statsFile:
    statsRecords = [ line.strip() for line in statsFile ]
    statsRecords = [ line.split('\t') for line in statsRecords if len(line) > 0 ]
    statsHeaderLine = statsRecords[0]
    statsRecords = statsRecords[1:]

invCountHeader = 'InversionCount' if 'InversionCount' in statsHeaderLine else 'ExpInversionCount'

trueVec = [ int(rec[statsHeaderLine.index('NumTrue')]) for rec in statsRecords ]
falseVec = [ int(rec[statsHeaderLine.index('NumFalse')]) for rec in statsRecords ]

assert len(trueVec) <= numAlarms
assert trueVec[-1] <= numTrue

if finishPlot:
    assert trueVec[-1] == numTrue
    while len(trueVec) < numAlarms:
        trueVec.append(trueVec[-1])
        falseVec.append(falseVec[-1] + 1)

assert len(trueVec) == len(falseVec)
fracTrueVec = [ trueVec[i] / (trueVec[i] + falseVec[i]) for i in range(0, numAlarms) ]
fracFalseVec = [ 1 - ft for ft in fracTrueVec ]

########################################################################################################################
# 3. Draw plot

fig, ax1 = plt.subplots()

# 3a. Draw yield curve

xindices = list(range(0, numAlarms))
lineFalseFrac = ax1.plot(xindices, fracFalseVec, linewidth=1)

# 3b. Draw scatter plot

ax2 = ax1.twinx()

markerArea=0.20
markerLineWidth=0.1
markerFillAlpha=0.75
labColor='b'
unlabColor='r'

ps = [ (iterIndex, rank) for iteration in enumerate(hmap) \
                         for (iterIndex, iterVals) in (iteration,) \
                         for (rank, val) in enumerate(iterVals) \
                         if val == Status.LabTrue ]
xs = [ p[0] for p in ps ]
ys = [ p[1] for p in ps ]
labelledPts = ax2.scatter(xs, ys, \
                          s=markerArea, linewidth=markerLineWidth, \
                          facecolors=labColor, alpha=markerFillAlpha, edgecolors=labColor, \
                          label='Labelled')

ps = [ (iterIndex, rank) for iteration in enumerate(hmap) \
                         for (iterIndex, iterVals) in (iteration,) \
                         for (rank, val) in enumerate(iterVals) \
                         if val == Status.UnlabTrue ]
xs = [ p[0] for p in ps ]
ys = [ p[1] for p in ps ]
unlabelledPts = ax2.scatter(xs, ys, \
                            s=markerArea, linewidth=markerLineWidth, \
                            facecolors='none', edgecolors=unlabColor, \
                            label='Unlabelled')

# 3c. Draw axes

ax1.set_xlim(xmin=0, xmax=numIters)
ax1.set_xlabel('Number of alarms inspected')
ax1.set_ylim(ymin=0, ymax=1.0)
ax1.set_ylabel('Fraction of false positives')

ax2.set_ylim(ymin=0, ymax=numAlarms)
ax2.set_ylabel('Rank')
ax2.invert_yaxis()

legend = ax2.legend((labelledPts, unlabelledPts), ('Labelled', 'Unlabelled'), loc='lower right')
legend.legendHandles[0]._sizes = [ 100 * markerArea ]
legend.legendHandles[1]._sizes = [ 100 * markerArea ]

# 3d. Produce output

plt.savefig(outputFileName, bbox_inches='tight')
