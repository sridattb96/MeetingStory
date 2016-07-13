#coding=utf-8
import process
import main_pnas
import sys
import outputjson

process.main()
topicNum = 0
if len(sys.argv)>1:
    topicNum =  sys.argv[1]
main_pnas.main(topicNum)
outputjson.main()
print "finished processing"
