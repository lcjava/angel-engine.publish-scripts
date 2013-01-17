#!/usr/bin/env python

import sys
import os

scripts = ["angel_pack", "angel_doc", "angel_samples_mac"]

if len(sys.argv) < 2:
  print "Pass me a version number, yo."
  exit(1)

start_dir = os.getcwd()
for script in scripts:
    os.chdir(start_dir)
    __import__(script)

# eventually have this do auto-uploads
