#!/usr/bin/env python

import sys
import os
import subprocess
import time
import math
import json

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
FILENAME = "%s%s" % (config["base_name"], sys.argv[1])
REPO = config["repository"]

# get a clean version of the latest code
print "Exporting code..."
do_quietly(['hg', 'clone', REPO, FILENAME])
do_quietly(['rm', '-rf', os.path.join(FILENAME, ".hg")])

# make changes for various distros
# print "Setting up distributions..."
# for dist in config["distros"].iterkeys():
#     print "\t" + dist.capitalize() + ":"
#     dist_dir = FILENAME + "-" + dist
#     # copy the trunk
#     print "\t\tCopying..."
#     do_quietly(['cp', '-R', FILENAME, dist_dir])
#     os.chdir(dist_dir)
#     # perform the deletions
#     print "\t\tDeleting..."
#     for deletion in config["distros"][dist]["deletions"]:
#         do_quietly(['rm', '-rf', deletion])
#     os.chdir("..")
#     # zip it up, remove the original directory
#     print "\t\tZipping..."
#     do_quietly(['zip', '-r9', dist_dir + ".zip", dist_dir])
#     print "\t\tCleaning..."
#     do_quietly(['rm', '-rf', dist_dir])

# zip, clean up original
print "\tFull Distro:"
print "\t\tZipping..."
do_quietly(['zip', '-r9', FILENAME + ".zip", FILENAME])
if not os.path.exists(config["output_dir_name"]):
	os.mkdir(config["output_dir_name"])
do_quietly(['mv', FILENAME + ".zip", os.path.join(config["output_dir_name"], FILENAME + ".zip")])
print "\t\tBuilding IntroGame..."
os.chdir(os.path.join(FILENAME, "Code"))
do_quietly(['xcodebuild', '-workspace', 'GameJam-Mac.xcworkspace', '-scheme', 'IntroGame', '-configuration', 'Release'])
os.chdir("IntroGame/Published")
zipName = FILENAME + "-IntroGame-Mac.zip"
do_quietly(['zip', '-r9', zipName, "IntroGame"])
do_quietly(['mv', zipName, os.path.join("..", "..", "..", "..", config["output_dir_name"], zipName)])
os.chdir(os.path.join("..", "..", "..", ".."))
print "\t\tCleaning..."
do_quietly(['rm', '-rf', FILENAME])

# script timer
finish = timer()
seconds = finish - start
minutes = 0
if seconds >= 60:
    minutes = seconds / 60
    seconds = seconds % 60
print "\n\nScript took %i:%02d." % (minutes, seconds)

# # resulting file sizes
# print "File sizes:"
# # distros = list(config["distros"].iterkeys())
# distros = list()
# distros.insert(0, "")
# for dist in distros:
#     if len(dist) > 0:
#         dist_zip = FILENAME + "-" + dist + ".zip"
#     else:
#         dist_zip = FILENAME + ".zip"
#     size_string = "\t" + dist_zip
#     if len(dist) > 0:
#         size_string += "\t\t"
#     else:
#         size_string += "\t\t\t"
#     file_size = os.path.getsize(dist_zip)
#     units = ["bytes", "KB", "MB", "GB", "TB"]
#     if file_size < 1024:
#       size_string += "%i %s" % (file_size, units[0])
#     else:
#         max_exp = len(units) - 1
#         file_size = float(file_size)
#         exponent = int(math.log(file_size) / math.log(1024))
#         if exponent > max_exp:
#             exponent = max_exp
#         file_size /= 1024 ** exponent
#         size_string += "%.1f %s" % (file_size, units[exponent])
#     print size_string

