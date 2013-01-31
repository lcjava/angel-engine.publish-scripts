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

def zipdir(directory, filename):
    do_quietly(['zip', '-r9', filename, directory])

# load configuration data
DISTRO_CONFIG_FILENAME = "pub_config.json"
config_data_file = open(DISTRO_CONFIG_FILENAME, "r")
config_data = config_data_file.read()
config_data_file.close()
config = json.loads(config_data)
REPO = config["repository"]

UPLOAD_DIR = config["output_dir_name"]
SAMPLES_DIR = "Angel-%s-Samples-Mac" % (sys.argv[1])
SYNC_PATH = "Angel-" + sys.argv[1]
START_DIR = os.getcwd()
SAMPLE_BRANCHES = ["samples-1", "samples-2"]


for dir_check in [UPLOAD_DIR, SAMPLES_DIR]:
    if not os.path.exists(dir_check):
        os.makedirs(dir_check)

if not os.path.exists(SYNC_PATH):
    print "Pulling latest repository...",
    do_quietly(['hg', 'clone', REPO, SYNC_PATH])
    print "done."

# build and grab IntroGame
os.chdir(os.path.join(SYNC_PATH))
do_quietly(['xcodebuild', '-workspace', 'GameJam-Mac.xcworkspace', '-scheme', 'IntroGame', '-configuration', 'Release'])
shutil.move(os.path.join("IntroGame", "Published", "IntroGame"), os.path.join("..", "..", SAMPLES_DIR, "IntroGame"))

for sample in SAMPLE_BRANCHES:
    print "Building", sample
    shutil.rmtree("ClientGame")
    do_quietly(['hg', 'revert', 'ClientGame'])
    do_quietly(['hg', 'up', sample])
    zipdir("ClientGame", "ClientGame.zip")
    do_quietly(['xcodebuild', '-workspace', 'GameJam-Mac.xcworkspace', '-scheme', 'ClientGame', '-configuration', 'Release'])
    app_list = os.listdir(os.path.join("ClientGame", "Published"))
    if '.DS_Store' in app_list: 
        app_list.remove('.DS_Store')
    app_name = app_list[0]
    shutil.move(os.path.join("ClientGame", "Published", app_name), os.path.join("..", "..", SAMPLES_DIR, app_name))
    shutil.move("ClientGame.zip", os.path.join("..", "..", SAMPLES_DIR, app_name, app_name + "-source.zip"))


os.chdir(START_DIR)
zipdir(SAMPLES_DIR, os.path.join(UPLOAD_DIR, SAMPLES_DIR + ".zip"))
