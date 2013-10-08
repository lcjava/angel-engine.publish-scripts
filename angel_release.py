#!/usr/bin/env python

import sys
import os
import shutil

scripts = ["angel_pack", "angel_doc", "angel_samples_mac"]
files = ["Angel-%s.zip", "AngelDocs_%s.zip", "Angel-%s-DemoPack-Windows.zip", "Angel-%s-DemoPack-Mac.zip"]
download_dir = os.path.join("angel2d.com", "downloads")

if len(sys.argv) < 2:
    print "Pass me a version number, yo."
    exit(1)

start_dir = os.getcwd()
for script in scripts:
    os.chdir(start_dir)
    __import__(script)

os.chdir("up")
for filename in files:
    f = filename % (sys.argv[1])
    shutil.move(f, os.path.join(download_dir, f))