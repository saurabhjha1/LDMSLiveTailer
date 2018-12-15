#!/usr/bin/env/python
# useful for tailing the logfile in a subprocess
import time
import subprocess
import select
import threading, Queue, subprocess
tailq = Queue.Queue(maxsize=10000) # buffer at most 100 lines

def safe_div(x,y):
    if y==0: return 0
    return x/float(y)

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, logfile):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()
        self.logfile = logfile

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(StoppableThread,self).join(*args, **kwargs)

    def run(self):
        p = subprocess.Popen(["tail", "-f", self.logfile], stdout=subprocess.PIPE)
        while not self._stop_event.is_set():
            line = p.stdout.readline()
            tailq.put(line)
        p.terminate()
        print("stopped!")

