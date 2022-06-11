#!/usr/bin/python3
import _thread
import queue
import time

from NadTuner import NadTuner

Tuner = NadTuner()
myqueue = queue.Queue(maxsize=100)


def sample_rds(rds):
    # ps = None
    while 1:
        response = Tuner.__read_bytes__()

        if response[1] == 27:
            if response[2] == 2:
                ps = 'No Rds'
            else:
                ps = response[2:10].decode('utf-8', errors='ignore')
            rds.put(ps)


# Define a function for the thread
def print_time(delay, rds):
    ps='Empyt'
    while True:
        # print(queue.get())
        print(rds.qsize())
        for a in range(rds.qsize()):
            ps = rds.get()
        print("RDS PS: %s  %s" % (ps, time.ctime(time.time())))
        time.sleep(2)


# Create two threads as follows
try:
    _thread.start_new_thread(sample_rds, (myqueue,))
    _thread.start_new_thread(print_time, (5, myqueue))
except:
    print("Error: unable to start thread")

while 1:
    time.sleep(1)
