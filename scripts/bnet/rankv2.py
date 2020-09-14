import os
from graph_tool import *
from graph_tool.topology import *
ncons=os.environ['RANKV2_CONS'] if 'RANKV2_CONS' in os.environ else None
DU2node={}
ug = Graph(directed=False)
def du2node(x):
	global DU2node,ug
	if x not in DU2node:
		DU2node[x]=ug.add_vertex()
	return DU2node[x]
def dfs(v,depth=0):
	global visited
	visited.add(v)
	rt=0.9**depth
	if depth<10:
		for x in v.out_neighbours():
			if x not in visited:
				rt+=dfs(x,depth+1)
	return rt
weight_cache={}
def load():
	global DU2node,ug
	if ncons is None:return
	i=0
	for x in open(ncons).readlines():
		x=x.split(': ')[1].split(', ')
		b=x[-1][:-1]
		for a in x[:-1]:
			ug.add_edge(du2node(a[4:]),du2node(b))
	global comp,hist,visited,weight_cache
	comp,hist=label_components(ug)
	for x in DU2node:
		if x.startswith('Alarm'):
			visited=set()
			weight_cache[x]=dfs(DU2node[x])
	mw=max(weight_cache.values())
	for x in weight_cache:
		weight_cache[x]=.1*weight_cache[x]/mw

def get_weight(n):
	# weight in [0,1]
	if ncons is None:return 1
	return weight_cache[n]
	#return .2*hist[comp[DU2node[n]]]/max(hist)
