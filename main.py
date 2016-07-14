import os
import sys
import argparse

def main():

	parser = argparse.ArgumentParser(description='Example with long option names')

	parser.add_argument('-m', action='store', dest='meeting_file', 
	                    help='Audio file of meeting')

	parser.add_argument('-s', nargs='+', action='store', dest='speakers', 
	                    help='Audio file of meeting')

	results = parser.parse_args()

	if results.speakers:
		str_speakers = ' '.join(results.speakers)
	else:
		print "You haven't specified any speakers!"

	os.system("python ./transcript_generator.py -m " + results.meeting_file + " -s " + str_speakers)
	os.system("python ./transcript_processor.py " + results.meeting_file)

	api_key = '63880a66d2c745419fdf3dce703d032c';
	meeting_audio = "./meeting/" + results.meeting_file + ".wav";
	audioCount = 0;
	voiceDict = {};

	


main()