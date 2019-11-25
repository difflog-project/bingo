#!/usr/bin/env python3

# Plots statistics from the interaction model, i.e the alarm carousel.

import math
import matplotlib.pyplot as plt
import sys

statsFileName = sys.argv[1]
outputFileName = sys.argv[2]

headerLine = []
records = []
with open(statsFileName) as statsFile:
    records = [ line.strip() for line in statsFile ]
    records = [ line.split('\t') for line in records if len(line) > 0 ]
    headerLine = records[0]
    records = records[1:]

invCountHeader = 'InversionCount' if 'InversionCount' in headerLine else 'ExpInversionCount'

ntrue = [ int(rec[headerLine.index('NumTrue')]) for rec in records ]
nfalse = [ int(rec[headerLine.index('NumFalse')]) for rec in records ]
fracTrue = [ float(rec[headerLine.index('Fraction')]) for rec in records ]
invCountStatic = [ float(rec[headerLine.index(invCountHeader)]) for rec in records ]

invCountDynamic = []
numFalse = 0
numInv = 0
for rec in records:
    if rec[headerLine.index('Ground')] == 'TrueGround':
        numInv = numInv + numFalse
    else:
        numFalse = numFalse + 1
    invCountDynamic.append(numInv)
print('Number of dynamic inversions: {0}'.format(numInv))

xindices = list(range(1, len(records) + 1))
fig, ax1 = plt.subplots()

lineNTrue = ax1.plot(xindices, ntrue, 'b', label='Number of true alarms', linewidth=2)
lineNFalse = ax1.plot(xindices, nfalse, 'r', label='Number of false alarms', linewidth=2)
ax1.set_ylim(ymin=0, ymax=50 * math.ceil(max(ntrue[-1], nfalse[-1]) / 50))
ax1.set_xlabel('Number of alarms inspected')
ax1.set_ylabel('Number of true / false alarms')
legend = ax1.legend(loc='upper left')

ax2 = ax1.twinx()
lineFracTrue = ax2.plot(xindices, fracTrue, 'g', label='Fraction of true alarms inspected', linewidth=2)
ax2.set_ylim(ymin=0, ymax=1)
ax2.set_ylabel('Fraction of true alarms inspected', color='g')

ax3 = ax1.twinx()
lineInvCountStatic = ax3.plot(xindices, invCountStatic, 'orange', label='Inversion count (Static)', \
                              linestyle='None', marker='.')
lineInvCountDynamic = ax3.plot(xindices, invCountDynamic, 'm', label='Inversion count (Dynamic)', linewidth=2)
ax3.set_ylim(ymin=0)
ax3.set_ylabel('Number of inversions', color='orange')
fig.subplots_adjust(right=0.75)
ax3.spines['right'].set_position(('axes', 1.2))

ax1.set_xbound(lower=0, upper=len(records))
lines = lineNTrue + lineNFalse + lineFracTrue + lineInvCountStatic + lineInvCountDynamic
labels = [ line.get_label() for line in lines ]
legend = ax1.legend(lines, labels, loc='center left', bbox_to_anchor=(1.5, 0.5))
# legend = ax2.legend(loc='upper right')

# fig.tight_layout()
# plt.show()
# plt.savefig(outputFileName, bbox_inches='tight')
plt.savefig(outputFileName, bbox_extra_artists=(legend,), bbox_inches='tight')
