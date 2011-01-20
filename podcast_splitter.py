# (c) 2011 Konstantin Yegupov, yk4ever@gmail.com

# MIT license, see http://opensource.org/licenses/mit-license.html


# USAGE: python podcast_splitter.py <original_file_name> [optional_title]
# Splits a long audio file (podcast track) into 5-minute fragments preceded by spoken introductions
# To be used with screenless MP3 players (e.g. iPod Shuffle)
# Results are dumped into ./out

# PREREQUISITES:
# command-line tools "sox", "espeak", "lame"

# On sane Linux systems (e.g. Ubuntu / Linux Mint) those can be installed like this:
# sudo apt-get install espeak lame sox libsox-fmt-mp3

# Probably can be adapted to run under Windows
# get required tools separately and make sure they are accessible by the PATH variable
# and fix slashes in paths



import glob, math, os.path, os
import subprocess
import sys

slice_len = 300

try:
    inp = sys.argv[1]
except IndexError:
    raise Exception("Please specify source file name")
    
basename =  os.path.splitext(os.path.split(sys.argv[1])[1])[0]   
try:
    title = sys.argv[2]
except IndexError:
    title = basename
    
try:
    subprocess.call("sox --version > /dev/null", shell=True)
except OSError:
    raise Exception("sox not installed")
    
try:
    subprocess.call("espeak -h > /dev/null", shell=True)
except OSError:
    raise Exception("espeak not installed")


try:
    subprocess.call("lame --help  > /dev/null", shell=True)
except OSError:
    raise Exception("lame not installed")

def trymkdir(s):
    try:
        os.mkdir(s)
    except OSError:
        pass
    

trymkdir("tmp")
trymkdir("out")
trymkdir("out"+os.sep+basename)
    
sout = subprocess.Popen("sox --i -D %s" % inp,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0]
secs = float(sout)
sout = subprocess.Popen("sox --i -c %s" % inp,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0]
channels = int(sout)

parts_count = int(math.ceil(secs/slice_len))
for start in range (0, int(math.ceil(secs)), slice_len):
    print " *** PROGRESS: %d%% ***" % (100*start/secs)
    i = start / slice_len
    dur = slice_len + 4
    if start>=4:
        start -= 4
        dur += 4
    if secs-start<dur:
        dur = secs-start
    fadein = 1 if i else 0
    print "sox: decoding audio and adding fades"
    my_proc = subprocess.Popen("sox %s tmp/part.wav trim %s %s fade %s %s 1"% (inp, start, dur, fadein, dur-2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sout = my_proc.communicate()[0]
    print "SOX: "+sout
    if sout.find("EOF")>-1:
        break
    print "espeak, sox: creating speech intro"
    text = "Part %s of %s" % (i+1, parts_count)
    if i==0 or (i%5==4):
        text += " in " + title
    subprocess.call("espeak -s 145 -w tmp/tmp.wav \"%s\""% (text), shell=True,)
    subprocess.call("sox tmp/tmp.wav tmp/tmp2.wav rate 44100 channels %s" % channels, shell=True)
    print "sox: concatenating intro and actual audio"
    subprocess.call("sox tmp/tmp2.wav tmp/part.wav tmp/partc.wav", shell=True)
    print "lame: encoding to mp3"
    subprocess.call("lame -S --nohist -V 6 tmp/partc.wav out/%s/%s_%03d.mp3" % (basename, basename, i+1), shell=True)
    os.unlink("tmp/partc.wav")
    
