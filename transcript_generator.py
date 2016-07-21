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

def get_api_key():
	return '63880a66d2c745419fdf3dce703d032c'


def get_duration(audioPath):
	with contextlib.closing(wave.open(audioPath,'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)
	    return duration;


def create_id_profile():
	api_key = get_api_key()

	url = 'https://api.projectoxford.ai/spid/v1.0/identificationProfiles';
	data = { "locale":"en-us" };
	headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': api_key};
	r = requests.post(url, data=json.dumps(data), headers=headers)
	time.sleep(5)

	res = r.json();
	return res["identificationProfileId"];


def create_enrollment(profile_id, voice):
	api_key = get_api_key()

	print "Training..."
	url = 'https://api.projectoxford.ai/spid/v1.0/identificationProfiles/' + profile_id + '/enroll';
	files = {'file': open(voice, 'rb')}
	headers = {'Ocp-Apim-Subscription-Key': api_key};
	r = requests.post(url, files=files, headers=headers)
	time.sleep(3)

	files = {'file': open(voice, 'rb')}
	r = requests.post(url, files=files, headers=headers)
	time.sleep(3)

	files = {'file': open(voice, 'rb')}
	r = requests.post(url, files=files, headers=headers)
	time.sleep(3)
	

def get_specific_profile(profile_id):
	api_key = get_api_key()

	url = 'https://api.projectoxford.ai/spid/v1.0/identificationProfiles/' + profile_id
	headers = {'Ocp-Apim-Subscription-Key': api_key};
	r = requests.get(url, headers=headers)
	return r.json()


def getOperationStatus(url):
	api_key = get_api_key()

	headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': api_key};
	r = requests.get(url, headers=headers)
	return r.json()


def speechRecognition(song, start, end):
	segment = song[start:end] 
	filename = "speech.wav"

	segment.export(filename, format="wav")
	r = sr.Recognizer()
	with sr.AudioFile(filename) as source:
	    audio = r.record(source) # this is for speech -> text
	try:
		text = r.recognize_google(audio);
		os.remove(filename)
		print text
		return text
	except sr.UnknownValueError:
	    print("Google Speech Recognition could not understand audio")
	    os.remove(filename)
	    return ""
	except sr.RequestError as e:
	    print("Could not request results from Google Speech Recognition service; {0}".format(e))
	    os.remove(filename)
	    return ""


def speakerRecognition(song, start, end, inc, voiceDict):
	segment = song[start:end]
	limit = int(math.ceil(63/inc));
	for i in range(0, limit):
		segment += song[start:end]
	# filename = filepath + str(x) + ".wav" # this is for identifying speaker
	filename = "speaker.wav"
	segment.export(filename, format="wav")
	name = identifySpeaker(voiceDict, filename) 
	os.remove(filename)
	return name;


def identifySpeaker(voiceDict, voice_sample):
	api_key = get_api_key()

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
			# print opStatus
			if opStatus['processingResult']:
				if opStatus['processingResult']['identifiedProfileId'] != "00000000-0000-0000-0000-000000000000":
					name = voiceDict[opStatus['processingResult']['identifiedProfileId']]
					break
				else:
					if opStatus['processingResult']['identifiedProfileId'] == "00000000-0000-0000-0000-000000000000":
						name = "Unknown Speaker"
						break
		else:
			print "Error: The key 'Operation-Location' doesn't exist in r.headers."
			exit(1)

	print "This is " + name + "'s voice."
	return name


def split_list(a_list):
    half = len(a_list)/2
    return a_list[:half], a_list[half:]


def train_speakers(speaker_arr, voice_dict):
	"""
	Trains each speaker specified in the command. 
	"""
	for i in range(0, len(speaker_arr)):
		speaker_name = speaker_arr[i]
		speaker_path = "./training/" + speaker_arr[i] + "_voice.wav"
		if os.path.exists(speaker_path):
			
			# enroll speaker
			profile_id = create_id_profile();
			create_enrollment(profile_id, speaker_path);

			# verify that speaker is enrolled
			json_obj = get_specific_profile(profile_id)
			if json_obj["enrollmentStatus"] == 'Enrolled':
				print speaker_name + " has been enrolled."
				voice_dict[profile_id] = speaker_name;
			else:
				print json_obj
				print "Something went wrong with path '" + speaker_path + "'...try again."
				exit(1)
		else:
			print "The path '" + speaker_path + "' doesn't exist...try again"
			exit(1)


def create_transcript(meeting_path, voice_dict):
	song = AudioSegment.from_wav(meeting_path)

	count = 0
	inc = 5;
	start = 0;
	end = inc * 1000;

	duration = get_duration(meeting_path)
	f = open("transcript.txt", 'w')

	d = datetime.datetime.fromtimestamp(os.path.getmtime(meeting_path))

	while True:
		print "From " + str(start/1000) + " to " + str(end/1000)

		text = speechRecognition(song, start, end);
		name = speakerRecognition(song, start, end, inc, voice_dict)

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
		count += 1

	print "Transcript completed!"

