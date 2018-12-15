#!/usr/bin/env python
import time 
bufsize = 1
f = open('/tmp/testnic.csv', 'w', buffering=bufsize)
for line in open("./metric_set_nic.1544886846", 'r'):
	time.sleep(0.1)
	f.write(line)