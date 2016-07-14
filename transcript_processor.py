import requests
import json
import wave
import time
import sys
import os
import contextlib
import speech_recognition as sr
import wave
import contextlib
import xlwt
import datetime
import shutil
import math

from pydub import AudioSegment
from tinytag import TinyTag
from os import path
from shutil import copyfile

# get length of file
def file_len(myfile):
    with open(myfile) as f:
   		return len(f.readlines())

def createfolder(datestring):

	print "creating folder..."
	
	# create folder
	dirname = "./project/data/" + datestring
	if os.path.exists(dirname):
		shutil.rmtree(dirname)
	os.makedirs(dirname)
	
	# write in index.txt
	indexFile = "./project/data/index.txt"
	rows = file_len(indexFile)
	with open(indexFile, "a") as myfile:
		myfile.write(str(rows + 1) + "\t" + datestring + "\n")
	
	# generate transcript (copy from current dir to folder)
	copyfile("./transcript.txt", dirname + "/transcript.txt")
	copyfile("./header.json", dirname + "/header.json")
	os.remove("./transcript.txt")
	os.remove("./header.json")

	# call run.py
	os.chdir("./project/tot")
	os.system("python run.py 10")

	# call script.py
	os.chdir("../../")
	os.system("python ./transcript_analyzer.py " + dirname)

def generateHeader(meeting_audio, monthdayyear):

	arr = meeting_audio.split('/')
	meetingArr = arr[len(arr)-1].split('.')[0].split('_');
	meetingName = ' '.join(meetingArr);
	monthArr = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	meetingDate = monthArr[int(monthdayyear[0])] + ' ' + monthdayyear[1] + ', ' + '20' + monthdayyear[2];

	# create json object
	header_json = {};
	header_json["title"] = meetingName;
	header_json["date"] = meetingDate;

	# save data to json file
	with open('./header.json', 'w') as f:
	    json.dump(header_json, f)

# MAIN SCRIPT ------------------------------------------------------------------------

meeting_audio = "./meeting/" + sys.argv[1] + ".wav";

# handle timestamps
monthdayyear = time.strftime('%m %d %y', time.gmtime(os.path.getmtime(meeting_audio))).split(' ');
timestamp = time.ctime(path.getctime(meeting_audio)).split(' ');

# print timestamp
month = monthdayyear[0]
day = monthdayyear[1]
year = monthdayyear[2]
times = timestamp[-2].split(':')
hour = times[0]
minute = times[1]
second = times[2]
d = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
datestring = year + month + day + hour + minute + second;

createfolder(datestring)

