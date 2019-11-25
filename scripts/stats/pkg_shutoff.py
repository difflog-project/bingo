#!/usr/bin/env python

# Arguments:
# 1. oracle_queries.txt
# 2. racePairs.txt
# 3. ground_truth (true bugs)
# 4. Level, "pkg" pkg-level, or "file" file-level shutoff.
# 5. Optionally, "copy" print the table as one column to copy easily.
# ./pkg_shutoff.py chord_output_mln-datarace-oracle/oracle_queries.txt chord_output_mln-datarace-oracle/racePairs_cs.txt hsqldb.gt pkg [copy]
import os
import sys
import re

oracle_queries = sys.argv[1]
race_pairs = sys.argv[2]
ground_truth = sys.argv[3]
level = sys.argv[4]
if len(sys.argv) > 5:
    printer = sys.argv[5]
else:
    printer = None

all_alarms = []
all_bugs = []
num_to_pkg = {}
def add_num(num, d):
    num_to_pkg[num] = d

with open(race_pairs, 'r') as f:
    for line in f:
        l = line.split('  ')
        num0 = l[0].split(':')[0]
        num1 = l[1].split(':')[0]
        file0 = l[0].split(':')[1]
        file1 = l[1].split(':')[1]
        dir0 = os.path.dirname(file0)
        dir1 = os.path.dirname(file1)
        if level == "pkg":
            add_num(num0, dir0)
            add_num(num1, dir1)
        elif level == "file":
            add_num(num0, file0)
            add_num(num1, file1)
        else:
            assert(False)
pkg_to_alarm = {}
pkg_to_bug = {}
def add_pkg_to_alarm(pkg):
    if pkg in pkg_to_alarm:
        pkg_to_alarm[pkg] = pkg_to_alarm[pkg] + 1
    else:
        pkg_to_alarm[pkg] = 1

def add_pkg_to_bug(pkg):
    if pkg in pkg_to_bug:
        pkg_to_bug[pkg] = pkg_to_bug[pkg] + 1
    else:
        pkg_to_bug[pkg] = 1

def add_pair(l, r, bug=False):
    pkg_l = num_to_pkg[l]
    pkg_r = num_to_pkg[r]
    if pkg_l == pkg_r:
        if bug:
            add_pkg_to_bug(pkg_l)
        else:
            add_pkg_to_alarm(pkg_l)
    else:
        if bug:
            add_pkg_to_bug(pkg_l)
            add_pkg_to_bug(pkg_r)
        else:
            add_pkg_to_alarm(pkg_l)
            add_pkg_to_alarm(pkg_r)

with open(oracle_queries, 'r') as f:
    for line in f:
        m = re.search(r"([0-9]+),([0-9]+)", line)
        (l, r) = (m.group(1), m.group(2))
        add_pair(l, r)
        all_alarms.append({'name': "(" + l + ',' + r + ")", 'pkg': [num_to_pkg[l], num_to_pkg[r]]})
    print(pkg_to_alarm)

with open(ground_truth, 'r') as f:
    for line in f:
        m = re.search(r"([0-9]+),([0-9]+)", line)
        (l, r) = (m.group(1), m.group(2))
        add_pair(l, r, True)
        all_bugs.append({'name': "(" + l + ',' + r + ")", 'pkg': [num_to_pkg[l], num_to_pkg[r]]})
#print(true_alarms)

l = list(pkg_to_alarm.items())
l.sort(key=lambda x: x[1], reverse=True)
def pretty_print():
    print('%50s\t%8s\t%8s' % ("Package","Alarms","Bugs"))
    for x in l:
        pkg = x[0]
        alarms = x[1]
        if pkg in pkg_to_bug:
            bugs = pkg_to_bug[pkg]
        else:
            bugs = 0
        print('%50s\t%8s\t%8s' % (pkg,alarms,bugs))

def column_print():
    print("Package")
    for x in l:
        print(x[0])
    print("Alarms")
    for x in l:
        print(x[1])
    print("Bugs")
    for x in l:
        if x[0] in pkg_to_bug:
            bugs = pkg_to_bug[x[0]]
        else:
            bugs = 0
        print(bugs)

if printer == 'copy':
    column_print()
else:
    pretty_print()

print('Total Alarm: {0}'.format(len(all_alarms)))
print('True  Alarm: {0}'.format(len(all_bugs)))

if len(sys.argv) > 6:
    filtered_alarms = [ a for a in all_alarms if not a['pkg'][0] in sys.argv[4:] and not a['pkg'][1] in sys.argv[4:] ]
    filtered_bugs = [ a for a in all_bugs if not a['pkg'][0] in sys.argv[4:] and not a['pkg'][1] in sys.argv[4:] ]
    print('Filtered Alarm: {0}'.format(len(filtered_alarms)))
    print('Filtered True Alarm: {0}'.format(len(filtered_bugs)))
