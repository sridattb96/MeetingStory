import os
import sys
import argparse
import transcript_generator
import organizer
import transcript_processor

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
		exit(1)

	voice_dict = {};
	meeting_path = "./meeting/" + results.meeting_file + ".wav";

	# # train speakers
	transcript_generator.train_speakers(results.speakers, voice_dict)

	# # generate transcript
	transcript_generator.create_transcript(meeting_path, voice_dict)

	# create folder and header
	organizer.create_header(meeting_path, results.meeting_file)
	dirname = organizer.create_folder(meeting_path)

	# process transcript
	os.chdir("./project/tot")
	os.system("python run.py 10")
	os.chdir("../../")

	transcript_processor.get_user_contribution(dirname)






main()