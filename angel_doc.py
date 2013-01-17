#!/usr/bin/env python

import sys
import os
import subprocess
import time
import json
import math
import markowik

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
FILENAME = "%s%s" % (config["base_name"], sys.argv[1])
DOCS_FILENAME = "%s%s" % (config["doc_base_name"], sys.argv[1])
ANGEL_PATH = config["angel_path"]
REPO = config["repository"]
IGNORE = config["doc_ignore_paths"]
PATH_TO_DOC = config["doc_data_path"]
LOCAL_PATH_TO_DOC = config["local_doc_data_path"]

# print os.path.join('..', config["output_dir_name"], config["doc_hosted_html_output_name"])
# sys.exit(0)

if not os.path.exists(config["output_dir_name"]):
    do_quietly(['mkdir', config["output_dir_name"]])

if not os.path.exists(FILENAME):
    print "Exporting code..."
    do_quietly(['hg', 'clone', REPO, FILENAME])
    # do_quietly(['rm', '-rf', os.path.join(FILENAME, ".hg")])

# create front page for Google Code page
with open(os.path.join(FILENAME, "Code", "README.txt"), 'r') as readme_file: markdown_text = readme_file.read()

insertion_marker = """

Getting Started
---------------"""

downloads_text = """

Downloads
---------
* **[Angel %s](http://angel-engine.googlecode.com/files/Angel-%s.zip)**: Our active development branch, which runs on Windows, Mac OS X, iOS, and Linux.
* **[Angel Documentation](http://angel-engine.googlecode.com/files/AngelDocs_%s.zip)**: The generated documentation from the %s codebase, linked above. Contains HTML and PDF versions for maximal offline viewing enjoyment. 
* **IntroGame**: Compiled versions of the example code, which shows off basic functionality. All the code is well-commented and modular, so you can download the source (above) and see how each example is implemented.
    * [Windows IntroGame](http://angel-engine.googlecode.com/files/Angel-%s-IntroGame-Windows.zip)
    * [Mac IntroGame](http://angel-engine.googlecode.com/files/Angel-%s-IntroGame-Mac.zip)"""
downloads_text = downloads_text % (sys.argv[1], sys.argv[1], sys.argv[1], sys.argv[1], sys.argv[1], sys.argv[1])

screenshots_text = """

Screenshots
-----------
Some screenshots of the demo application."""
for shot_type in ["Console", "Intervals", "Multitouch", "Particles", "Pathfinding"]:
    screenshots_text += "\n\n**%s**\n\n[![%s](http://wiki.angel-engine.googlecode.com/hg/images/%s_t.png)](http://wiki.angel-engine.googlecode.com/hg/images/%s.png)]" % (shot_type, shot_type, shot_type.lower(), shot_type.lower())

markdown_text = markdown_text.replace(insertion_marker, screenshots_text + downloads_text + insertion_marker)

google_code_text = markowik.convert(markdown_text)
output_file = open(os.path.join(config["output_dir_name"], "google_front_page.txt"), 'w')
output_file.write(google_code_text)
# output_file.write(markdown_text)
output_file.close()

# generate docs
print "Generating documentation package..."
os.chdir(os.path.join(FILENAME, "Code", "Angel"))

dox = open("Doxyfile", "r")
dox_text = dox.read()
dox.close()
dox_text = dox_text.replace("PROJECT_NAME           = Angel\n", "PROJECT_NAME           = \"Angel " + sys.argv[1] + "\"\n")
dox = open("Doxyfile", "w")
dox.write(dox_text)
dox.close()

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
do_quietly(['mv', 'docs', os.path.join("..", "..", "..", DOCS_FILENAME)])
os.chdir(os.path.join("..", "..", ".."))
do_quietly(['zip', '-r9', DOCS_FILENAME + ".zip", DOCS_FILENAME])
do_quietly(['mv', DOCS_FILENAME + ".zip", os.path.join(config["output_dir_name"], DOCS_FILENAME + ".zip")])

# generate HTML documenation for upload
print "Generating the hosted documentation..."
os.chdir(os.path.join(FILENAME, "Code", "Angel"))
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
for filePath, repls in replacements.iteritems():
    rawFile = open(os.path.join('docs/html', filePath), "r")
    text = rawFile.read()
    rawFile.close()

    for orig, new in repls.iteritems():
        text = text.replace(orig, new)
    rawFile = open(os.path.join('docs/html', filePath), "w")
    rawFile.write(text)
    rawFile.close()
do_quietly(['mv', 'docs/html', os.path.join('..', '..', '..', config["output_dir_name"], config["doc_hosted_html_output_name"])])

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
