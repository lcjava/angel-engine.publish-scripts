#!/usr/bin/env python

import sys
import os
import subprocess
import time
import math
import json
import shutil
import glob
import contextlib
import zipfile

if (sys.platform[:3] == 'win'):
    timer = time.clock
else:
    timer = time.time

start = timer()

# a simple way to execute quietly
def do_quietly(exec_array):
    subprocess.call(exec_array, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

def get_quietly(exec_array):
    return subprocess.Popen(exec_array, stdout=subprocess.PIPE).communicate()[0]


# load configuration data
DISTRO_CONFIG_FILENAME = "pub_config.json"
config_data_file = open(DISTRO_CONFIG_FILENAME, "r")
config_data = config_data_file.read()
config_data_file.close()
config = json.loads(config_data)
REPO = config["repository"]

OUTPUT_DIR = "Angel-%s-Samples-Windows" % (sys.argv[1])
VS_DIR = r"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin"
START_DIR = os.getcwd()
SAMPLE_BRANCHES = ["samples-1", "samples-2"]


if not os.path.exists('windows-angel'):
    print "Pulling latest repository...",
    do_quietly(['hg', 'clone', REPO, 'windows-angel'])
    print "done."

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

def zipdir(basedir, archivename):
    with contextlib.closing(zipfile.ZipFile(archivename, "w", zipfile.ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(basedir):
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir)+len(os.sep):]
                z.write(absfn, zfn)

## set up paths
# os.chdir(VS_DIR)
# os.system("vcvars32")
# os.chdir(START_DIR)

# build and grab IntroGame
os.chdir(os.path.join("windows-angel"))
os.system("msbuild /nologo /p:Configuration=Release")

shutil.move(os.path.join("IntroGame", "Published"), os.path.join("..", "..", OUTPUT_DIR, "IntroGame"))

for sample in SAMPLE_BRANCHES:
    print "Building", sample
    shutil.rmtree("ClientGame")
    do_quietly(['hg', 'revert', 'ClientGame'])
    do_quietly(['hg', 'up', sample])
    shutil.rmtree(os.path.join("ClientGame", "platforms", "ios")) 
    shutil.rmtree(os.path.join("ClientGame", "platforms", "mac"))
    shutil.rmtree(os.path.join("ClientGame", "ClientGame.xcodeproj"))
    shutil.rmtree(os.path.join("ClientGame", "ClientGame-iOS.xcodeproj"))
    os.remove(os.path.join("ClientGame", "Makefile"))
    zipdir("ClientGame", "ClientGame.zip")
    os.system("msbuild /nologo /p:Configuration=Release")
    os.chdir(os.path.join("ClientGame", "Published"))
    exe_list = glob.glob("*.exe")
    exe_name = exe_list[0] # we know there's only one
    exe_name = exe_name[:-4] # trim the ".exe"
    os.chdir(os.path.join("..", ".."))
    shutil.move(os.path.join("ClientGame", "Published"), os.path.join("..", "..", OUTPUT_DIR, exe_name))
    shutil.move("ClientGame.zip", os.path.join("..", "..", OUTPUT_DIR, exe_name, exe_name + "-source.zip"))


os.chdir(START_DIR)
zipdir(OUTPUT_DIR, OUTPUT_DIR + ".zip")
