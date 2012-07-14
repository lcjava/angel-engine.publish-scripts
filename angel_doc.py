#!/usr/bin/env python

import sys
import os
import subprocess
import time
import json
import math

if (sys.platform[:3] == 'win'):
    timer = time.clock
else:
    timer = time.time

start = timer()

# a simple way to execute quietly
def do_quietly(exec_array):
    subprocess.call(exec_array, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

# a simple way to execute and get output
def get_quietly(exec_array):
    return subprocess.Popen(exec_array, stdout=subprocess.PIPE).communicate()[0]

# load configuration data
DISTRO_CONFIG_FILENAME = "pub_config.json"
config_data_file = open(DISTRO_CONFIG_FILENAME, "r")
config_data = config_data_file.read()
config_data_file.close()
config = json.loads(config_data)
ANGEL_PATH = config["angel_path"]
REPO = config["repository"]
OUTPUT = config["doc_output"]
IGNORE = config["doc_ignore_paths"]
PATH_TO_DOC = config["doc_data_path"]
LOCAL_PATH_TO_DOC = config["local_doc_data_path"]

# print os.path.join('..', config["output_dir_name"], config["doc_hosted_html_output_name"])
# sys.exit(0)

if not os.path.exists(config["output_dir_name"]):
    do_quietly(['mkdir', config["output_dir_name"]])

# sync, but we only want the Angel directory minus "Libraries"
print "Exporting docs..."
do_quietly(['svn', 'export', '-N', REPO + ANGEL_PATH, OUTPUT])
dirs = get_quietly(['svn', 'ls', REPO + ANGEL_PATH]).split()
for directory in dirs:
    if (directory[-1] != "/"):
        continue
    if directory in IGNORE:
        continue
    do_quietly(['svn', 'export', REPO + ANGEL_PATH + "/" + directory, OUTPUT + "/" + directory])

# My lord, this is ignorant. This is just my local "build docs", script, 
#  though, so damn the torpedoes. 
do_quietly(['svn', 'export', REPO + PATH_TO_DOC, LOCAL_PATH_TO_DOC])

# # generate docs
print "Generating documentation package..."
os.chdir(OUTPUT)
do_quietly(['doxygen'])

# add license information to PDF output
os.chdir("docs/latex")
for rep_file in config["doxygen_replacements"].iterkeys():
    ind = open(rep_file, "r")
    ind_text = ind.read()
    ind.close()
    orig_text = config["doxygen_replacements"][rep_file]["orig"]
    new_text = config["doxygen_replacements"][rep_file]["new"]
    ind_text = ind_text.replace(orig_text, new_text)
    ind = open(rep_file, "w")
    ind.write(ind_text)
    ind.close()

# make the PDF, move it to the right place
do_quietly(['make', 'pdf'])
os.chdir("..")
do_quietly(['mv', 'latex/refman.pdf', config["doc_pdf_output_name"]])
do_quietly(['rm', '-rf', 'latex'])

# make the HTML index file
index = open(config["doc_html_output_name"], "w")
index.write(config["doc_html_contents"])
index.close()

# do the replacements in output HTML
replacements = config["doc_html_replacements"]
for filePath, repls in replacements.iteritems():
    rawFile = open(os.path.join('html', filePath), "r")
    text = rawFile.read()
    rawFile.close()

    for orig, new in repls.iteritems():
        text = text.replace(orig, new)
    rawFile = open(os.path.join('html', filePath), "w")
    rawFile.write(text)
    rawFile.close()

# switcheroo and zip
os.chdir("..")
filename = config["doc_base_name"] + sys.argv[1]
do_quietly(['mv', 'docs', filename])
do_quietly(['zip', '-r9', filename + ".zip", filename])
do_quietly(['mv', filename + ".zip", os.path.join('../', config["output_dir_name"], filename + ".zip")])

# generate HTML documenation for upload
print "Generating the hosted documentation..."
dox = open("Doxyfile", "r")
dox_text = dox.read()
dox.close()
replacements = config["doc_hosted_html_replacements"]
for orig, new in replacements.iteritems():
    dox_text = dox_text.replace(orig, new)
dox = open("Doxyfile", "w")
dox.write(dox_text)
dox.close()
do_quietly(['doxygen'])
replacements = config["doc_html_replacements"]
print(os.getcwd())
for filePath, repls in replacements.iteritems():
    rawFile = open(os.path.join('docs/html', filePath), "r")
    text = rawFile.read()
    rawFile.close()

    for orig, new in repls.iteritems():
        text = text.replace(orig, new)
    rawFile = open(os.path.join('docs/html', filePath), "w")
    rawFile.write(text)
    rawFile.close()
do_quietly(['mv', 'docs/html', os.path.join('..', config["output_dir_name"], config["doc_hosted_html_output_name"])])

# cleanup
print "Cleaning up documentation..."
os.chdir("..")
do_quietly(['rm', '-rf', config["doc_output"]])

# Cleaning up the ignorance
do_quietly(['rm', '-rf', config['local_doc_data_path'].split('/')[0]])

# script timer
finish = timer()
seconds = finish - start
minutes = 0
if seconds >= 60:
    minutes = seconds / 60
    seconds = seconds % 60
print "\n\nScript took %i:%02d;" % (minutes, seconds), 

# file_size = os.path.getsize(os.path.join(config["output_dir_name"], filename + ".zip"))
# units = ["bytes", "KB", "MB", "GB", "TB"]
# if file_size < 1024:
#     print "resulting doc file was %i %s." % (file_size, units[0])
# else:
#     max_exp = len(units) - 1
#     file_size = float(file_size)
#     exponent = int(math.log(file_size) / math.log(1024))
#     if exponent > max_exp:
#         exponent = max_exp
#     file_size /= 1024 ** exponent
#     print "resulting documentation file was %.1f %s" % (file_size, units[exponent])
