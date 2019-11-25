#!/usr/local/bin/python3

import networkx as nx
import matplotlib.pyplot as plt
import os
import sys
import re

oracle_queries = sys.argv[1]
ground_truth = sys.argv[2]

G = nx.Graph()

with open(oracle_queries, 'r') as f:
    for line in f:
        m = re.search(r"([0-9]+),([0-9]+)", line)
        (l, r) = (m.group(1), m.group(2))
        G.add_edge(l, r)

true_set = set()
with open(ground_truth, 'r') as f:
    for line in f:
        m = re.search(r"([0-9]+),([0-9]+)", line)
        (l, r) = (m.group(1), m.group(2))
        G.add_edge(l, r, color='red')
        true_set.add((l,r))

scc = list(nx.connected_component_subgraphs(G))
sorted_scc = [c for c in sorted(scc, key=lambda x: x.number_of_edges(), reverse=True)]
sorted_size = [len(c) for c in sorted(scc, key=len, reverse=True)]
total_alarms = 0
total_bugs = 0
for g in sorted_scc:
    alarms = 0
    bugs = 0
    for (x,y) in g.edges():
        if 'color' in g[x][y]:
            bugs = bugs + 1
        alarms = alarms + 1
    if bugs > 0:
        print('Alarms : {0}, Bugs : {1}'.format(alarms, bugs))
    else:
        print('Alarms : {0}'.format(alarms))
    total_alarms = total_alarms + alarms
    total_bugs = total_bugs + bugs
print('Total Alarms : {0}, Total Bugs : {1}'.format(total_alarms, total_bugs))
