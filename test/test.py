#!/usr/bin/env python
import sys 
import time 
bufsize = 1
f = open('/tmp/test', 'w', buffering=bufsize)
for line in open(sys.argv[1], 'r'):
	time.sleep(1)
	f.write(line)