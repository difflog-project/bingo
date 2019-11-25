#!/usr/bin/env python3

# Given a file containing roadrunner output, extract a unique set of races reported in this run. 
# ./extract.py < rr_out.txt > race.txt 


import logging
import re
import sys

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

########################################################################################################################
# 0. Prelude

# allRaces is a set of sets. Each element of allRaces is a set of two racing accesses
allRaces = set()

########################################################################################################################
# 1. Accept Input 

rrOut = [line.strip() for line in sys.stdin]


########################################################################################################################
# 2. Extract racing pairs of accesses 

def getAccess(s):
    accessParts = [ part.strip() for part in re.split(' ',parts[1]) ]
    assert(len(accessParts) >= 3)
    accessType = accessParts[0]  # 'Write' or 'Read'
    srcLoc = accessParts[2]
    # In the source location, keep only the filename and line number; remove the column number (for now).
    if srcLoc.count(':') == 2: 
        srcLoc = srcLoc[:srcLoc.rindex(':')]
    return (accessType, srcLoc)


lineCnt = 0
while lineCnt < len(rrOut):
    line = rrOut[lineCnt]
    if 'Previous Op: ' in line:
        # get the access type (read or write) and the source location of the first racing access
        parts = [ part.strip() for part in re.split('Op: ', line) ]
        assert(len(parts) == 2)
        access1 = getAccess(parts[1])
        if ('NullLoc' in access1[1]):
            # Unable to handle the case of NullLoc in Previous Op.
            lineCnt += 1
            continue 

        # get the access type (read or write) and the source location of the second racing access
        lineCnt += 1
        line = rrOut[lineCnt]
        parts = [ part.strip() for part in re.split('Op: ', line) ]
        assert(len(parts) == 2)
        # Note: there is a spelling error in the roadrunner output.
        assert('Currrent' in parts[0])
        access2 = getAccess(parts[1])
        if ('NullLoc' in access2[1]):
            # Extract source location from the stack trace.
            lineCnt += 1
            line = rrOut[lineCnt]
            assert('Stack:' in line)
            # Bypass the entries in the stack trace that show call locations in fasttrack
            while 'fasttrack_with_locs' in line:
                lineCnt += 1
                line = rrOut[lineCnt]
            while 'RREventGenerator.java' in line:
                lineCnt += 1
                line = rrOut[lineCnt]
            while 'rr_get_' in line:
                lineCnt += 1
                line = rrOut[lineCnt]
            while 'rr_put_' in line:
                lineCnt += 1
                line = rrOut[lineCnt]

            # Now, the current frame in the stack trace belongs to the application.
            # Extract source file and line number from this frame.
            parts = [ part.strip() for part in re.split('\(', line) ]
            parts[1] = parts[1][:-1]
            access2 = (access2[0], parts[1])
        r = set()
        r.add(access1)
        r.add(access2)
        race = frozenset(r)
        allRaces.add(race)
    lineCnt += 1

logging.info('Discovered {0} races.'.format(len(allRaces)))


########################################################################################################################
# 3. Print output 

# Need to convert frozensets to lists for convenient printing
allRaces1 = ([list(x) for x in allRaces])
for r in allRaces1:
    print('race {0} {1} {2} {3}'.format(r[0][0], r[0][1], r[1][0], r[1][1]))

