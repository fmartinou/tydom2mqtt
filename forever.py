#!/usr/bin/env python3
from subprocess import Popen
import sys

filename = sys.argv[1]
while True:
    print("\nStarting " + filename)
    p = Popen("python3 -u " + filename, shell=True)
    p.wait()