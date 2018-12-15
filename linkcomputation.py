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
import itertools
# header 
# Time,Time_usec,ProducerName,component_id,job_id,aries_rtr_id



## global variables
aries_metric_deltas = {}
aries_metric_prev = {}
aries_ts_prev = {}
aries_out_metrics = {}
metrics = {
}
curr_time = 0
tiles = []

# expected output 
# 0     "Time", "CId", "Aries", "dt", "DFH2N", "DSN2H", "DS2FN2H", "DFN2P", "DSN2P", "DS2FN2P", "DHPG"

def func():
# function that handles new log line
	global metrics, aries_metric_deltas, aries_metric_prev, aries_ts_prev, curr_time, aries_out_metrics, tiles
	cols = tailq.get().strip().decode('unicode-escape').split(',')
	aries_id = cols[5]
	tcurr = int(cols[0].split('.')[0])
	if aries_id not in aries_metric_deltas:
		aries_metric_deltas[aries_id] = copy.deepcopy(metrics)
		aries_metric_prev[aries_id] = copy.deepcopy(metrics)
		r_c = itertools.product(range(5), range(8))
		aries_out_metrics[aries_id] = {}
		for m in r_c:
			aries_out_metrics[aries_id]["df_{}_{}".format(m[0], m[1])] = 0.0
			aries_out_metrics[aries_id]["ds_{}_{}".format(m[0], m[1])] = 0.0
			aries_out_metrics[aries_id]["s2f_{}_{}".format(m[0], m[1])] = 0.0
		aries_out_metrics[aries_id]["dt"] = 0.0
		aries_ts_prev[aries_id]  =  0
		curr_time = tcurr
	else:
		if tcurr > aries_ts_prev[aries_id]:
			for mKey in metrics:
				aries_metric_deltas[aries_id][mKey] = int(cols[metrics[mKey]]) - aries_metric_prev[aries_id][mKey]
				aries_metric_prev[aries_id][mKey] = int(cols[metrics[mKey]])
			
			# format output
			# dt
			dt = tcurr - aries_ts_prev[aries_id]
			aries_out_metrics[aries_id]["dt"] = dt
			# df/dt
			r_c  = list(itertools.product(range(5), range(8)))
			for m in r_c:
				# total delta flits
				rc_sum = 0
				for vc in range(8):
					rc_sum += \
						aries_metric_deltas[aries_id]["AR_RTR_{}_{}_INQ_PRF_INCOMING_FLIT_VC{}".format(m[0], m[1], vc)]
				# df for r_c
				aries_out_metrics[aries_id]["df_{}_{}".format(m[0], m[1])] = \
						safe_div(rc_sum, dt)
				# ds for r_c
				aries_out_metrics[aries_id]["ds_{}_{}".format(m[0], m[1])] = \
						safe_div(aries_metric_deltas[aries_id]["AR_RTR_{}_{}_INQ_PRF_ROWBUS_STALL_CNT".format(m[0], m[1])], dt)
				# s2f for r_c
				aries_out_metrics[aries_id]["s2f_{}_{}".format(m[0],m[1])] = \
						safe_div(aries_metric_deltas[aries_id] ["AR_RTR_{}_{}_INQ_PRF_ROWBUS_STALL_CNT".format(m[0], m[1])], rc_sum)
	aries_ts_prev[aries_id] = tcurr
	if curr_time < tcurr:
#		if len(tiles) > 0:
#			arr = numpy.array([[nic_out_metrics[nid][mKey] for mKey in sorted(nic_out_metrics[nid])] for nid in sorted(nic_out_metrics) if nid in nodes])
#			arr1 = numpy.array([[nic_metric_deltas[nid][mKey] for mKey in sorted(nic_metric_deltas[nid])] for nid in sorted(nic_metric_deltas) if nid in nodes])
#		else:
#			arr = numpy.array([[nic_out_metrics[nid][mKey] for mKey in sorted(nic_out_metrics[nid])] for nid in sorted(nic_out_metrics)])
		print("time", "aries_id", "dt", "tile", "df", "ds", "s2f")
		if len(tiles) == 0:
			tiles = list(itertools.product(range(5), range(8)))
		for tile in tiles:
			print(
				tcurr, aries_id, aries_out_metrics[aries_id]["dt"],
				str(tile[0]) + "_" + str(tile[1]), 
				aries_out_metrics[aries_id]["df_{}_{}".format(tile[0], tile[1])],
				aries_out_metrics[aries_id]["ds_{}_{}".format(tile[0], tile[1])],
				aries_out_metrics[aries_id]["s2f_{}_{}".format(tile[0], tile[1])],
			)
		curr_time = tcurr
	return


def main():
	global metrics, tiles
	# initialize metrics, i.e., which metrics do we want
	r_c_vc = itertools.product(range(5), range(8), range(8))
	for m in r_c_vc:
		metrics["AR_RTR_{}_{}_INQ_PRF_INCOMING_FLIT_VC{}".format(m[0], m[1], m[2])] = 0.0
	r_c = itertools.product(range(5), range(8))
	for m in r_c:
		metrics["AR_RTR_{}_{}_INQ_PRF_ROWBUS_STALL_CNT".format(m[0], m[1])] = 0.0

	parser = argparse.ArgumentParser()
	parser.add_argument("--logfile")
	parser.add_argument("--headerfile")
	parser.add_argument("--tilelist", required = False)
	args = parser.parse_args()
	# parse header
	header_line = ""
	with open(args.headerfile) as hfh:
		header_line = hfh.readline().strip()
	header = header_line.split(',')
	for mKey in metrics.keys():
		metrics[mKey] = header.index(mKey)
	# parse nid list
	if args.tilelist != None:
		tiles = [ x.split("_") for x in args.tilelist.split(",")]
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
