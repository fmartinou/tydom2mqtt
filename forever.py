#!/usr/bin/env python3

from subprocess import Popen
import sys

filename = sys.argv[1]
while True:
    print("\nStarting " + filename)
    p = Popen("python3 " + filename, shell=True)
    p.wait()


    #thanks https://ep.gnt.md/index.php/how-to-restart-python-script-after-exception-and-run-it-forever/