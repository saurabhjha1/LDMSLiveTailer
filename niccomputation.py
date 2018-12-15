#!/usr/bin/env python

import os 
import sys
import numpy
import argparse
import copy
from util import StoppableThread, safe_div, tailq
import threading
import signal 
from pprint import pprint
# header 
# Time,Time_usec,ProducerName,component_id,job_id,app_id,aries_rtr_id



## global variables
nic_metric_deltas = {}
nic_metric_prev = {}
nic_ts_prev = {}
nic_out_metrics = {}
metrics = {
	"AR_NIC_NETMON_ORB_EVENT_CNTR_REQ_FLITS": 0,
	"AR_NIC_NETMON_ORB_EVENT_CNTR_REQ_STALLED": 0,
	"AR_NIC_RSPMON_PARB_EVENT_CNTR_PI_STALLED" : 0,
	"AR_NIC_RSPMON_PARB_EVENT_CNTR_IOMMU_PKTS": 0,
	"AR_NIC_RSPMON_PARB_EVENT_CNTR_PI_FLITS"  : 0,
	"AR_NIC_RSPMON_PARB_EVENT_CNTR_PI_PKTS"  : 0
}
curr_time = 0
nodes = []

# expected output 
# 0     "Time", "CId", "Aries", "dt", "DFH2N", "DSN2H", "DS2FN2H", "DFN2P", "DSN2P", "DS2FN2P", "DHPG"

def func():
# function that handles new log line
	global metrics, nic_metric_deltas, nic_metric_prev, nic_ts_prev, curr_time, nic_out_metrics, nodes
	numeric_index_start = nId = 6
	cols = tailq.get().strip().decode('unicode-escape').split(',')
	nid = cols[2]
	aries_id = cols[6]
	tcurr = int(cols[0].split('.')[0])
	if nid not in nic_metric_deltas:
		nic_metric_deltas[nid] = copy.deepcopy(metrics)
		nic_metric_prev[nid] = copy.deepcopy(metrics)
		nic_out_metrics[nid] = {"aries_id": "", "dt":0, "df":0, "ds":0, "s2f":0, "dpif":0, "dprocs":0, "n2p":0, "hpg":0}
		nic_ts_prev[nid]  =  0
		curr_time = tcurr
	else:
		if tcurr > nic_ts_prev[nid]:
			for mKey in metrics:
				nic_metric_deltas[nid][mKey] = int(cols[metrics[mKey]]) - nic_metric_prev[nid][mKey]
				nic_metric_prev[nid][mKey] = int(cols[metrics[mKey]])
			# format output
			# dt
			dt = tcurr - nic_ts_prev[nid]
			nic_out_metrics[nid]["aries_id"] = aries_id
			nic_out_metrics[nid]["dt"] = dt
			# df/dt
			nic_out_metrics[nid]["ds"] = safe_div(nic_metric_deltas[nid]["AR_NIC_NETMON_ORB_EVENT_CNTR_REQ_STALLED"], dt)
			# ds/dt
			nic_out_metrics[nid]["df"] = safe_div(nic_metric_deltas[nid]["AR_NIC_NETMON_ORB_EVENT_CNTR_REQ_FLITS"], dt)
			#  s2f
			nic_out_metrics[nid]["s2f"] = safe_div(nic_metric_deltas[nid]["AR_NIC_NETMON_ORB_EVENT_CNTR_REQ_STALLED"], nic_metric_deltas[nid]["AR_NIC_NETMON_ORB_EVENT_CNTR_REQ_FLITS"])
			# dprocs/dt
			nic_out_metrics[nid]["dprocs"] = safe_div(nic_metric_deltas[nid]["AR_NIC_RSPMON_PARB_EVENT_CNTR_PI_STALLED"], dt)
			# dpif/dt
			nic_out_metrics[nid]["dpif"] = safe_div(nic_metric_deltas[nid]["AR_NIC_RSPMON_PARB_EVENT_CNTR_PI_FLITS"], dt)
			#  n2p
			nic_out_metrics[nid]["n2p"] = safe_div(nic_metric_deltas[nid]["AR_NIC_RSPMON_PARB_EVENT_CNTR_PI_STALLED"], nic_metric_deltas[nid]["AR_NIC_RSPMON_PARB_EVENT_CNTR_PI_FLITS"])
			#  hpg
			nic_out_metrics[nid]["hpg"] = safe_div(nic_metric_deltas[nid]["AR_NIC_RSPMON_PARB_EVENT_CNTR_IOMMU_PKTS"], nic_metric_deltas[nid] ["AR_NIC_RSPMON_PARB_EVENT_CNTR_PI_PKTS"])
	nic_ts_prev[nid] = tcurr
	if curr_time < tcurr:
#		if len(nodes) > 0:
#			arr = numpy.array([[nic_out_metrics[nid][mKey] for mKey in sorted(nic_out_metrics[nid])] for nid in sorted(nic_out_metrics) if nid in nodes])
#			arr1 = numpy.array([[nic_metric_deltas[nid][mKey] for mKey in sorted(nic_metric_deltas[nid])] for nid in sorted(nic_metric_deltas) if nid in nodes])
#		else:
#			arr = numpy.array([[nic_out_metrics[nid][mKey] for mKey in sorted(nic_out_metrics[nid])] for nid in sorted(nic_out_metrics)])
		print("time", "nid", "aries_id", "dt", "df", "ds", "s2f", "dpif", "dprocs", "n2p", "hpg")
		if len(nodes) == 0:
			nodes = nic_out_metrics.keys()
		for nid in nodes:
			print(
				tcurr, 
				nid,
                                nic_out_metrics[nid]["aries_id"],
				nic_out_metrics[nid]["dt"],
				nic_out_metrics[nid]["df"],
				nic_out_metrics[nid]["ds"],
				nic_out_metrics[nid]["s2f"],
				nic_out_metrics[nid]["dpif"],
				nic_out_metrics[nid]["dprocs"],
				nic_out_metrics[nid]["n2p"],
				nic_out_metrics[nid]["hpg"]
			)
		curr_time = tcurr
	return


def main():
	global metrics, nodes
	parser = argparse.ArgumentParser()
	parser.add_argument("--logfile")
	parser.add_argument("--headerfile")
	parser.add_argument("--nidlist", required = False)
	args = parser.parse_args()
	# parse header
	header_line = ""
	with open(args.headerfile) as hfh:
		header_line = hfh.readline().strip()
	header = header_line.split(',')
	for mKey in metrics.keys():
		metrics[mKey] = header.index(mKey)
	# parse nid list
	if args.nidlist != None:
		for nidTuple in args.nidlist.split(","):
			if '-' in nidTuple:
				s_nid = int(nidTuple.split('-')[0])
				s_end = int(nidTuple.split('-')[1]) + 1
				for nid in range(s_nid, s_end):
					nodes.append('nid{:0>5d}'.format(nid))
			else:
				nodes.append('nid{:0>5d}'.format(int(nidTuple)))
	# start tailing the logfile
	tailer = StoppableThread(args.logfile)
	tailer.start()
	while True:
		try:
			func()
		except KeyboardInterrupt:
			tailer.stop()
			print("keyboard interrupt occurred")
			sys.exit(1)


if __name__ == "__main__":
	main()
