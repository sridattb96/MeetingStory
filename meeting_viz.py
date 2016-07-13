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

	os.system("python ./main.py -m " + results.meeting_file + " -s " + str_speakers)
	os.system("python ./main2.py " + results.meeting_file)


main()