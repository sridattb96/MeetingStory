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

def file_len(myfile):
    with open(myfile) as f:
   		return len(f.readlines())


def create_folder(meeting_path):

	datestring = time.strftime('%Y%m%d%H%M%S', time.gmtime(os.path.getmtime(meeting_path)))

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
	
	# copy transcript and header file to folder
	copyfile("./transcript.txt", dirname + "/transcript.txt")
	copyfile("./header.json", dirname + "/header.json")
	# os.remove("./transcript.txt")
	# os.remove("./header.json")

	# call run.py
	# os.chdir("./project/tot")
	# os.system("python run.py 10")

	# # call script.py
	# os.chdir("../../")
	# os.system("python ./transcript_analyzer.py " + dirname)

	return dirname

def create_header(meeting_path, meeting_file):

	timestamp = time.gmtime(os.path.getmtime(meeting_path))

	header_json = {};
	header_json["title"] = meeting_file.replace("_", " ")
	header_json["date"] = time.strftime("%B %d, %Y", timestamp)

	# save data to json file
	with open('./header.json', 'w') as f:
	    json.dump(header_json, f)

