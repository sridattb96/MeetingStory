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
import argparse

from pydub import AudioSegment
from tinytag import TinyTag
from os import path
from shutil import copyfile

# get duration of audio file
def getDuration(audioPath):
	with contextlib.closing(wave.open(audioPath,'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)
	    return duration;

# create identification profile
def createIdProfile():
	url = 'https://api.projectoxford.ai/spid/v1.0/identificationProfiles';
	data = { "locale":"en-us" };
	headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': api_key};
	r = requests.post(url, data=json.dumps(data), headers=headers)
	res = r.json();
	res["identificationProfileId"];
	return res["identificationProfileId"];

# create enrollment
def createEnrollment(profileId, voice):

	print "Training..."
	url = 'https://api.projectoxford.ai/spid/v1.0/identificationProfiles/' + profileId + '/enroll';
	files = {'file': open(voice, 'rb')}
	headers = {'Ocp-Apim-Subscription-Key': api_key};
	r = requests.post(url, files=files, headers=headers)
	# print getOperationStatus(r.headers['Operation-Location'])

	files = {'file': open(voice, 'rb')}
	r = requests.post(url, files=files, headers=headers)

	files = {'file': open(voice, 'rb')}
	r = requests.post(url, files=files, headers=headers)

	time.sleep(5)

# get all profiles
def getAllProfiles():
	url = 'https://api.projectoxford.ai/spid/v1.0/identificationProfiles';
	headers = {'Ocp-Apim-Subscription-Key': api_key};
	r = requests.get(url, headers=headers)
	print r.json()

# get specific profile
def getSpecificProfile(profileId):
	url = 'https://api.projectoxford.ai/spid/v1.0/identificationProfiles/' + profileId
	headers = {'Ocp-Apim-Subscription-Key': api_key};
	r = requests.get(url, headers=headers)
	return r.json()

# get operation status
def getOperationStatus(url):
	headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': api_key};
	r = requests.get(url, headers=headers)
	return r.json()

def speechRecognition(start, end):
	segment = song[start:end] 
	filename = filepath + "speech.wav"
	segment.export(filename, format="wav")
	r = sr.Recognizer()
	with sr.AudioFile(filename) as source:
	    audio = r.record(source) # this is for speech -> text
	try:
		text = r.recognize_google(audio);
		os.remove(filename)
		return text
	except sr.UnknownValueError:
	    print("Google Speech Recognition could not understand audio")
	    return ""
	except sr.RequestError as e:
	    print("Could not request results from Google Speech Recognition service; {0}".format(e))
	    return ""

	os.remove(filename)
	return text

def speakerRecognition(start, end, inc):
	segment = song[start:end]
	limit = int(math.ceil(63/inc));
	for i in range(0, limit):
		segment += song[start:end]
	filename = filepath + str(x) + ".wav" # this is for identifying speaker
	segment.export(filename, format="wav")
	name = identifySpeaker(voiceDict, filename) 
	os.remove(filename)
	return name;

# identify speaker
def identifySpeaker(voiceDict, voice_sample):
	# print "Identifying speakers..."

	voiceStrings = ''
	for key in voiceDict:
		voiceStrings = voiceStrings + key + ','
	voiceStrings = voiceStrings[:-1]

	url = 'https://api.projectoxford.ai/spid/v1.0/identify?identificationProfileIds=' + voiceStrings;
	files = {'file': open(voice_sample, 'rb')}
	headers = {'Ocp-Apim-Subscription-Key': api_key};
	r = requests.post(url, files=files, headers=headers)
	# print r.headers

	while True:
		if 'Operation-Location' in r.headers:
			time.sleep(5)
			opStatus = getOperationStatus(r.headers['Operation-Location']);
			time.sleep(3)
			print opStatus
			if opStatus['processingResult']:
				if opStatus['processingResult']['identifiedProfileId'] != "00000000-0000-0000-0000-000000000000":
					name = voiceDict[opStatus['processingResult']['identifiedProfileId']]
					break
				else:
					if opStatus['processingResult']['identifiedProfileId'] == "00000000-0000-0000-0000-000000000000":
						name = "Unknown Speaker"
						break
		else:
			time.sleep(5)
			print "try again"

	print "This is " + name + "'s voice."
	return name

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
	# os.remove("./transcript.txt")
	# os.remove("./header.json")

	# call run.py
	os.chdir("./project/tot")
	os.system("python run.py 10")

	# call script.py
	os.chdir("../../")
	os.system("python ./script.py " + dirname)

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

def split_list(a_list):
    half = len(a_list)/2
    return a_list[:half], a_list[half:]

# MAIN SCRIPT ------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Example with long option names')

parser.add_argument('-m', action='store', dest='meeting_file', 
                    help='Audio file of meeting')

parser.add_argument('-s', nargs='+', action='store', dest='speakers', 
                    help='Audio file of meeting')

results = parser.parse_args()

# global var
# api_key = '49438e90c042498d91fbf9a5268bf40d';
api_key = '63880a66d2c745419fdf3dce703d032c';
meeting_audio = "./meeting/" + results.meeting_file + ".wav";
audioCount = 0;
voiceDict = {};

# take input
# input = raw_input('training data: ')
trainingArr = results.speakers
trainingArr = ["./training/" + s + "_voice.wav" for s in trainingArr]
# trainingArr = input.split(' ')
for i in range(0, len(trainingArr)):
	if os.path.exists(trainingArr[i]):
		
		# get audio file path
		audioFilePath = trainingArr[i].split('/')
		audioFileName = audioFilePath[len(audioFilePath)-1]
		audioFileArr = audioFileName.split('_')

		# enroll speaker
		id = createIdProfile();
		speakerName = audioFileArr[0]
		createEnrollment(id, trainingArr[i]);

		# verify that speaker is enrolled
		while(True):
			json_obj = getSpecificProfile(id)
			if json_obj["enrollmentStatus"] == 'Enrolled':
				print speakerName + " has been enrolled."
				voiceDict[id] = speakerName;
				audioCount = audioCount + 1;
				break
			else:
				print json_obj
				print "Something went wrong with path '" + trainingArr[i] + "'...try again."
				exit()
	else:
		print "The path '" + trainingArr[i] + "' doesn't exist...try again"

print meeting_audio
song = AudioSegment.from_wav(meeting_audio)
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), meeting_audio).split('.')
filepath = AUDIO_FILE[0]

x = 0;
inc = 5;
start = 0;
end = inc * 1000;

duration = getDuration(meeting_audio)
outputFile = "transcript.txt"
f = open(outputFile, 'w')

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

while True:

	x += 1;
	print "From " + str(start/1000) + " to " + str(end/1000);

	# speech & speech recognition
	text = speechRecognition(start, end);
	name = speakerRecognition(start, end, inc)

	start += inc * 1000;
	end += inc * 1000;

	# write transcript 
	if start < duration * 1000 and end < duration * 1000:
		f.write(str(d) + "\t" + name + "\t" + text + "\n")
	else:
		A = text.split(' ')
		B, C = split_list(A)
		f.write(str(d) + "\t" + name + "\t" + ' '.join(B) + "\n")
		f.write(str(d) + "\t" + name + "\t" + ' '.join(C) + "\n")
		break;

	d += datetime.timedelta(seconds = inc)

print "Transcription successful!"

generateHeader(meeting_audio, monthdayyear);


