#!/usr/bin/env python3

# Given a directory containing the combined files produced by the driver.py AC command, 0.out, 1.out, 2.out, ..., plots
# the scatter plot of the distribution of true alarms.

# Arguments:
# 1. Directory containing the combined files produced by the driver.py AC command, 0.out, 1.out, 2.out, ...
# 2. Name of the output file.
# 3. 'finish'. Optional argument. In case the driver.py AC run is still incomplete, but all true positives have already
#    been produced, then completes the run.

# ./scripts/stats/hdot-simple.py ~/Scratch/acombined output.pdf [finish]

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

combinedDirName = sys.argv[1]
outputFileName = sys.argv[2]
finishPlot = 'finish' in sys.argv[3:]

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
# 3. Draw plot

# 3a. Draw yield curve

xindices = list(range(0, numAlarms + 1))
numLabTrue = [ len([ v for v in vec if v == Status.LabTrue ]) for vec in hmap ]
lineTrueNum, = plt.fill(xindices + [ xindices[-1] + 1, xindices[-1] + 1 ], \
                        numLabTrue + [ numLabTrue[-1], 0 ], label='Inspected True Alarms', alpha=0.75)
plt.plot(xindices, numLabTrue, linewidth=1)

# 3b. Draw scatter plot

markerArea=0.20
markerLineWidth=0.1
markerFillAlpha=0.75
labColor='b'
unlabColor='r'

ps = [ (iterIndex, rank) for iteration in enumerate(hmap) \
                         for (iterIndex, iterVals) in (iteration,) \
                         for (rank, val) in enumerate(iterVals) \
                         if val == Status.UnlabTrue ]
xs = [ p[0] for p in ps ]
ys = [ p[1] for p in ps ]
unlabelledPts = plt.scatter(xs, ys, \
                            s=markerArea, linewidth=markerLineWidth, \
                            facecolors='none', edgecolors=unlabColor, \
                            label='Uninspected True Alarms')

# 3c. Draw axes

plt.xlim(xmin=0, xmax=numIters)
plt.xlabel('Number of alarms inspected')
plt.ylim(ymin=0, ymax=numAlarms)
plt.ylabel('Rank')

legend = plt.legend((lineTrueNum, unlabelledPts), ('Inspected True Alarms', 'Uninspected True Alarms'), loc='upper right')
legend.legendHandles[1]._sizes = [ 100 * markerArea ]

# 3d. Produce output

plt.savefig(outputFileName, bbox_inches='tight')
