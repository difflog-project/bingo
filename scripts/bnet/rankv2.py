import os
PT=os.environ['RANKV2_PT'] if 'RANKV2_PT' in os.environ else None
ptprob={}
def load():
	if PT is None:return
	global ptprob
	for x in open(PT).readlines():
		x=x.split()
		# Assuming init prob not too small
		if '0.' in x[1]:
			ptprob[x[-1]]=float(x[1])
def get_weight(n):
	return ptprob[n] if n in ptprob else 0
