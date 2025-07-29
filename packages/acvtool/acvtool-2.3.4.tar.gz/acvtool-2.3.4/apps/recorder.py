import os
import subprocess

def record(fpath):
    cmd = "adb exec-out getevent -lt /dev/input/event2 > {}".format(fpath)
    os.system(cmd)
    
print("Recording events into a text file.")
print("Press Ctrl+C to finalize...")
record("test.txt")