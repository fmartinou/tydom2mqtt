#!/usr/bin/env python3
from subprocess import Popen
import sys

while True:
    print("\nStarting forever script....")
    p = Popen("python3 -u main.py", shell=True)
    p.wait()