#!/usr/bin/env python

import sys

scripts = ["angel_doc", "angel_pack"]

if len(sys.argv) < 2:
  print "Pass me a version number, yo."
  exit(1)

for script in scripts:
  __import__(script)

# eventually have this do auto-uploads
