#!/usr/bin/env python3
import os
import subprocess as sp
import re
import sys
processes = []
def exec_cmd(cmd):
	result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
	return result.stdout, result.stderr

def concurrent_exec_cmd(cmd):
	print(cmd)
	p = sp.Popen(cmd)
	processes.append(p)

def get_nodes(nodes):
	nidlist = []
	tnodes = nodes.split(",")
	for tlist in tnodes:
		ncols= tlist.split('-')
		tstart = int(ncols[0])
		if len(ncols) > 1:
			tend = int(ncols[1])
		else:
			tend = tstart + 1
		#fnodes = map(lambda nid: 'nid{:0>5d}'.format(nid), range(tstart, tend+1))
		fnodes = map(lambda x: str(x), range(tstart, tend))
		nidlist.extend(fnodes)
	return nidlist

def main():
	logfile_nodes = [
	"nid00896",  "nid01280",  "nid01664",  "nid01665",  "nid02048",  "nid02049"
	]
	out, err  = exec_cmd("sinfo -p resv --state=alloc".split())
	nodes = get_nodes(re.search("nid\[(.*)\]", out.decode('utf-8')).groups(0)[0])	
	for ldms_nid in logfile_nodes:
		concurrent_exec_cmd(("python2 ../niccomputation.py --logfile /scratch1/ovis/csv/nid02049/metric_set_nic.1557730800  --headerfile /scratch1/ovis/csv/" +  ldms_nid + "/metric_set_nic.1557730800 --nidlist " + ",".join(nodes)).split())
		concurrent_exec_cmd(("python2 ../niccomputation.py --logfile /scratch1/ovis/csv/nid02049/metric_set_nic.1557730800  --headerfile /scratch1/ovis/csv/" +  ldms_nid + "/metric_set_nic.1557730800 --nidlist " + ",".join(nodes)).split())
	

	#out, err = concurrent_exec_cmd("python2 ./niccomputation.py --logfile /scratch1/ovis/csv/nid02049/metric_set_nic.1557730800  --headerfile /scratch1/ovis/csv/nid02049/metric_set_nic.1557730800 --nidlist 2668".split())

	for p in processes:
		p.wait()
if __name__ == "__main__":
	main()
