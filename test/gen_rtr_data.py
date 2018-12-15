#!/usr/bin/env python
import sys 
import time 
bufsize = 1
f = open('/tmp/testrtr.csv', 'w', buffering=bufsize)
for line in open("./metric_set_rtr_0_4_c.1544886846", 'r'):
	time.sleep(1)
	f.write(line)