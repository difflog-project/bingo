#!/usr/bin/env python3

# Given a directory containing the combined files produced by the driver.py AC command, 0.out, 1.out, 2.out, ..., plots
# the heat map of the distribution of true alarms.

# Plots the heat map of the distribution of true alarms.
# Arguments:
# 1. Directory containing hte combined files produced by the driver.py AC command, 0.out, 1.out, 2.out, ...
# 2. Name of the output file.
# 3. X-Axis type. 'xnum' or 'xper'. If 'xnum', the x-axis will say, 'Number of alarms inspected'. If 'xper', the x-axis
#    will say, 'Percentage of alarms inspected'.
# 4. plotfrac. If 0 <= plotfrac <= 1.0, indicates the fraction of the total iterations to present. If plotfrac < 0, then
#    only displays iterations until the last true positive is discovered.
# 5. 'finish'. Optional argument. In case the driver.py AC run is still incomplete, but all true positives have already
#    been produced, then completes the run.
# 6. 'vline'. Optional argument. If present, draws a vertical line at full rank.
# 7. 'hline'. Optional argument. If present, draws a horizontal line at full rank.

# ./scripts/stats/hmap.py ~/Scratch/acombined output.pdf xnum 1.0 [finish] [vline]

# The original FTP plot was plotted using:
# ./scripts/stats/hmap.py ~/Scratch/acombined output.pdf xnum 1.0 vline finish

# The 25, 50, and AD plots were generated using:
# ./scripts/stats/hmap.py ~/Scratch/acombined output25.pdf xper 0.25 hline finish
# ./scripts/stats/hmap.py ~/Scratch/acombined output50.pdf xper 0.50 hline finish
# ./scripts/stats/hmap.py ~/Scratch/acombined outputAD.pdf xper -1 hline finish

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
xtype = sys.argv[3]
plotfrac = float(sys.argv[4])
finishPlot = 'finish' in sys.argv[5:]
drawVline = 'vline' in sys.argv[5:]
drawHline = 'hline' in sys.argv[5:]

assert xtype == 'xnum' or xtype == 'xper'
assert plotfrac <= 1.0

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

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

numTrue = len([ v for v in hmap[0] if v == Status.LabTrue or v == Status.UnlabTrue ])
numAlarms = len(hmap[0])
numDiscoveredAtFullRank = len([v for v in hmap[numTrue] if v == Status.LabTrue ])
numIters = len(hmap)

if 0 <= plotfrac:
    numIters = math.ceil(numIters * plotfrac)
else:
    numIters = 0
    while Status.UnlabTrue in hmap[numIters]: numIters = numIters + 1
    plotfrac = numIters / len(hmap)
hmap = hmap[:numIters]

logging.info(numIters)
logging.info(numAlarms)
logging.info(plotfrac)
logging.info(len(hmap))

hmap = numpy.matrix([ [ PixVal[v] for v in col ] for col in hmap ]).getT()

matplotlib.rc('font', family='DejaVu Sans')

# From https://stackoverflow.com/a/18786106
def calculate_aspect(shape, extent):
    dx = abs(extent[1] - extent[0]) / float(shape[0])
    dy = abs(extent[3] - extent[2]) / float(shape[1])
    return dx / dy

shape = (numIters, numAlarms)
extent = (0, numIters, numAlarms, 0) if xtype == 'xnum' else (0, 100 * plotfrac, numAlarms, 0)
aspect=calculate_aspect(shape, extent)
logging.info('Aspect: {0}'.format(aspect))
hmap = plt.imshow(hmap, extent=extent, aspect=aspect, interpolation='none', cmap=cm.get_cmap('Accent', 4))

ax = plt.axes()
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')
ax.set_xlabel('Number of alarms inspected' if xtype == 'xnum' else 'Percentage of alarms inspected')
ax.set_ylabel('Rank')

if drawVline:
    extraYTicks = [ numDiscoveredAtFullRank ]
    ylim = ax.get_ylim()
    ax.set_yticks(list(ax.get_yticks()) + extraYTicks)
    ax.set_ylim(ylim)

    vlinePos = numTrue if xtype == 'xnum' else (100 * numTrue / numAlarms)
    textPos = (numTrue + 2) if xtype == 'xnum' else (100 * (numTrue + 2) / numAlarms)
    plt.text(textPos, numAlarms - 2, '{0} true alarms'.format(numTrue), rotation=90, ha='left', va='bottom')
    plt.axvline(vlinePos, color='k', linewidth=1)

if drawHline:
    extraYTicks = [ numTrue ]
    ylim = ax.get_ylim()
    ax.set_yticks(list(ax.get_yticks()) + extraYTicks)
    ax.set_ylim(ylim)
    plt.axhline(numTrue, color='k', linewidth=1)

cbar = plt.colorbar(hmap, ticks=[-3, -1, 1, 3])
cbar.ax.set_yticklabels(['Lab✗', 'Unlab✗', 'Unlab✓', 'Lab✓'])

plt.savefig(outputFileName, bbox_inches='tight', dpi=1000)
