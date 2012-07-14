import os
import sys
import subprocess
import time
import math

timer = time.time
start = timer()

def do_quietly(exec_array):
    subprocess.call(exec_array, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

def get_quietly(exec_array):
    return subprocess.Popen(exec_array, stdout=subprocess.PIPE).communicate()[0]


if not (os.path.exists("AppImageKit-8")):
    print("Unzipping AppImageKit...")
    do_quietly(['tar', 'xzf', 'AppImageKit-8.tar.gz'])
if not (os.path.exists("AppImageKit-8/AppImageAssistant")):
    print("Building AppImageKit...")
    os.chdir("AppImageKit-8")
    do_quietly(["make"])
    os.chdir("..")

# assumes we're alongside AngelTrunk and looking for IntroGame
PUBDIR = os.getcwd()
os.chdir("../angel-trunk/Code/IntroGame")
do_quietly(["make"])
os.chdir(PUBDIR)

os.system("mkdir IntroGame.appdir")
os.chdir("IntroGame.appdir")

os.system("mkdir -p usr/lib")
os.system("mkdir -p usr/bin")
os.system("cp ../../angel-trunk/Code/IntroGame/IntroGame usr/bin/IntroGame")
os.system("cp -R ../../angel-trunk/Code/IntroGame/Resources usr/")
os.system("cp -R ../../angel-trunk/Code/IntroGame/Config usr/")
os.system("cp -R ../../angel-trunk/Code/IntroGame/platforms/linux/angel.png ./IntroGame.png")
os.system("cp ../AppImageKit-8/AppRun ./")

dtop_file = open("IntroGame.desktop", "w")
dtop_file.write("[Desktop Entry]\nName=IntroGame\nExec=IntroGame\nIcon=IntroGame\nTerminal=false\nType=Application\n")
dtop_file.close()

lib_output = get_quietly(["ldd", "usr/bin/IntroGame"])

get = [
    "libIL.so.1",
    "libILU.so.1",
    "libILUT.so.1",
    "libmng.so.1"
]

for f in lib_output.splitlines():
    data = f.split()
    if data[0] in get:
        exec_string = "cp %s usr/lib/%s" % (data[2], data[0])
        os.system(exec_string)
        oldlink = data[2]
        newlink = oldlink.replace("/usr", "././")
        exec_string = "sed -i -e 's|%s|%s|g' usr/bin/IntroGame" % (oldlink, newlink)
        #print(exec_string)
        #os.system(exec_string)

os.system("sed -i -e 's|../Angel/Libraries/FMOD/lib/libfmodex.so|././././././././././././lib/libfmodex.so|g' usr/bin/IntroGame")
os.system("cp ../../angel-trunk/Code/Angel/Libraries/FMOD/lib/libfmodex.so usr/lib/libfmodex.so")

os.chdir(PUBDIR)
os.system("./AppImageKit-8/AppImageAssistant.appdir/package ./IntroGame.appdir ./IntroGame")
#os.system("rm -rf IntroGame.appdir")


finish = timer()
seconds = finish - start
minutes = 0
if seconds >= 60:
    minutes = seconds / 60
    seconds = seconds % 60
print "\n\nScript took %i:%02d;" % (minutes, seconds),

sys.exit(0)

filename = "IntroGame"

file_size = os.path.getsize(filename)
units = ["bytes", "KB", "MB", "GB", "TB"]
if file_size < 1024:
    print "resulting file was %i %s." % (file_size, units[0])
else:
    max_exp = len(units) -1
    file_size = float(file_size)
    exponent = int(math.log(file_size) / math.log(1024))
    if exponent > max_exp:
        exponent = max_exp
    file_size /= 1024 ** exponent
    print "resulting file was %.1f %" % (file_size, units[exponent])
