#coding=utf-8
import re
import time
import fileinput
from sets import Set
import random
import scipy.special
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from scipy.stats import beta
import pprint,pickle
import json
import process

wordcloud = {}
newwordcloud = {}
newwordcloud["clouds"] = []
topics = {}
startTimePoint = 0
endTimePoint = 0
timespan = 3600

def maxWordIndexOfTopic(phiz,nthtopic):
    index = -1
    maxWordWeight = 0
    for i in range(len(phiz)):
        if(phiz[i][nthtopic]>maxWordWeight):
            maxWordWeight = phiz[i][nthtopic]
            index = i
    return index,maxWordWeight

def getTimePoints(psi):
    xs = np.linspace(0,1,num=100000)
    ys =[]
    for i in range(len(psi)):
        ysi = [math.pow(1-x, psi[i][0]-1)*math.pow(x, psi[i][1]-1)/
                scipy.special.beta(psi[i][0],psi[i][1]) for x in xs]
        ys.append(ysi)
    #print len(psi)
    return xs,ys

#wordcloud divided by wordiz
def generateWordCloud(phi,words,num_topics,viz_threshold=9e-3):
    phi_viz = np.transpose(phi)
    words_to_display = ~np.all(phi_viz <= viz_threshold, axis = 1)
    words_viz = [words[i] for i in range(len(words_to_display)) if words_to_display[i]]
    phi_viz = phi_viz[words_to_display]
    wordcloud["clouds"] = []
    for i in range(num_topics):
        cloud = {}
        ixofitopic,wofitopic =  maxWordIndexOfTopic(phi_viz,i)
        cloud["topic"] = words_viz[ixofitopic]
        #cloud["ts_start"] = []
        #cloud["ts_end"] = []
        cloud["keywords"] = []
        for j in range(len(words_viz)):
            #if words_viz[j] != cloud["topic"]:
            keyword = {}
            keyword["name"] = words_viz[j]
            keyword["value"] = phi_viz[j][i]
            cloud["keywords"].append(keyword)
        wordcloud["clouds"].append(cloud)
    #print phi_viz
    #print words_viz
    #print wordcloud
    #except ts_start and ts_end

def getTopicsTimeRange(psi,ys,xs,totaltime):
    changeFlag = False
    topicIndex = -1
    maxValue = 0
    tempTopicIndex = -1
    for i in range(len(ys[0])):
        maxValue = 0
        for j in range(len(psi)):
            if ys[j][i] > maxValue:
                maxValue = ys[j][i]
                tempTopicIndex = j
        if tempTopicIndex != topicIndex:
            changeFlag = True
            if topicIndex != -1:
                wordcloud["clouds"][topicIndex]["ts_end"].append(int(xs[i-1]*totaltime))
            topicIndex = tempTopicIndex
        if changeFlag == True:
            wordcloud["clouds"][topicIndex]["ts_start"].append(int(xs[i]*totaltime))
            changeFlag = False
        if i == len(ys[0])-1:
            wordcloud["clouds"][topicIndex]["ts_end"].append(int(xs[i]*totaltime))
    #print totaltime


def generateTopics(wordcloud,startTimePoint,endTimePoint):
    topics["topics"] =[]
    for i in range(len(wordcloud["clouds"])):
        topic = {}
        topic["topic"] = wordcloud["clouds"][i]["topic"]
        topic["ts_start"] = wordcloud["clouds"][i]["ts_start"]
        topic["ts_end"] = wordcloud["clouds"][i]["ts_end"]
        topic["users"] = []
        topics["topics"].append(topic)

    #read users by time
    f = open("../data/201604100002.txt","rw")
    string = ""
    for line in f:
        string = string + line
    reg = r'(\d\d:\d\d)\t(.+?)\t(.+?)\n'
    data = re.compile(reg)
    datalist = data.findall(string)
    userSetlist = []
    for i in range(len(wordcloud["clouds"])):
        userSetlist.append(Set())
    for each in datalist:
        timestr = time.strptime("2016-4-10 00:"+each[0],"%Y-%m-%d %H:%M:%S")
        cur_time_span = int(time.mktime(timestr))-int(startTimePoint)
        for i in range(len(wordcloud["clouds"])):
            for j in range(len(wordcloud["clouds"][i]["ts_start"])):
                #print "0:"+str(wordcloud["clouds"][i]["ts_start"][j])+","+str(j)+","+str(i)
                if wordcloud["clouds"][i]["ts_start"][j] <= cur_time_span and cur_time_span <= wordcloud["clouds"][i]["ts_end"][j]:
                       # user = {}
                       # user["name"] = each[1]
                       # topic["users"].append(user)
                    userSetlist[i].add(each[1])
    #print userSetlist
    for i in range(len(topics["topics"])):
        for eachUser in userSetlist[i]:
            user = {}
            user["name"] = eachUser
            topics["topics"][i]["users"].append(user)

def combineOrNot(ys,ith,jth):
    combineThreshold = 100 #threshold needs vary
    diff = 0
    for i in range(len(ys[i])):
        diff = diff + math.pow(ys[ith][i]-ys[jth][i],2)
    if diff > combineThreshold:
        return False
    else:
        return True

#newwordcloud generated by wordcloud combing the key topic
def processWordCloud(psi,ys,xs,totaltime):
    #print totaltime
    newcloudlist = []
    changeFlag = False
    topicIndex = -1
    maxValue = 0
    tempTopicIndex = -1
    for i in range(len(ys[0])):
        maxValue = 0
        for j in range(len(psi)):
            if ys[j][i] > maxValue:
                maxValue = ys[j][i]
                tempTopicIndex = j
        if tempTopicIndex != topicIndex:
            changeFlag = True
            if topicIndex == -1:
                if len(newcloudlist) == 0:
                    newcloudlist.append({})
                    newcloudlist[0]["set"] = Set()
                    newcloudlist[0]["start"] = 0
                    newcloudlist[0]["end"] = None
        if changeFlag == True:
            if wordcloud["clouds"][topicIndex]["topic"] == wordcloud["clouds"][tempTopicIndex]["topic"]:
                #print newcloudlist,topicIndex,tempTopicIndex
                newcloudlist[-1]["set"].add(tempTopicIndex)
            else:
                newcloudlist[-1]["end"] = int(xs[i-1]*totaltime)
                #print topicIndex,tempTopicIndex
                if topicIndex != -1:
                    newcloudlist.append({})
                newcloudlist[-1]["set"] = Set()
                newcloudlist[-1]["set"].add(tempTopicIndex)
                newcloudlist[-1]["start"] = int(xs[i]*totaltime)
            topicIndex = tempTopicIndex
            changeFlag = False

        if i == len(ys[0])-1:
            #print totaltime
            newcloudlist[-1]["end"] = int(totaltime)
            #print newcloudlist[-1]["end"]
    #print newcloudlist
    for each in newcloudlist:
        cloud =  {}
        cloud["topic"] = wordcloud["clouds"][list(each["set"])[0]]["topic"]
        cloud["ts_start"] = each["start"]
        cloud["ts_end"] = each["end"]
        cloud["keywords"] = []
        for i in range(len(wordcloud["clouds"][0]["keywords"])):
            keyword = {}
            keyword["name"] = wordcloud["clouds"][0]["keywords"][i]["name"]
            value = 0
            for j in each["set"]:
                value = value + wordcloud["clouds"][j]["keywords"][i]["value"]
            value = value/len(each["set"])
            keyword["value"] = value
            if value >0:
                cloud["keywords"].append(keyword)
        newwordcloud["clouds"].append(cloud)
    for i in range(len(newwordcloud["clouds"])):
        cloudlen = len(newwordcloud["clouds"])
        if i < cloudlen:
            #print i,len(newwordcloud["clouds"])
            if newwordcloud["clouds"][i]["ts_end"]-newwordcloud["clouds"][i]["ts_start"]<30:
                del newwordcloud["clouds"][i]
    #print newwordcloud

#generate new topic
def generateNewTopics(startTimePoint,endTimePoint,index=""):
    topics["topics"] =[]
    for i in range(len(newwordcloud["clouds"])):
        topic = {}
        topic["topic"] = newwordcloud["clouds"][i]["topic"]
        topic["ts_start"] = newwordcloud["clouds"][i]["ts_start"]
        topic["ts_end"] = newwordcloud["clouds"][i]["ts_end"]
        topic["users"] = []
        topic["color"] = "#DBF1FD"
        topics["topics"].append(topic)

    #read users by timestamp
    f = open("../data/"+index+"/transcript.txt","rw")
    string = ""
    for line in f:
        string = string + line
    reg = r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)\t(.+?)\t(.+?)\n'
    data = re.compile(reg)
    datalist = data.findall(string)
    userSetlist = []
    for i in range(len(newwordcloud["clouds"])):
        userSetlist.append(Set())
    for each in datalist:
        timestr = time.strptime(each[0],"%Y-%m-%d %H:%M:%S")
        cur_time_span = int(time.mktime(timestr))-int(startTimePoint)
        for i in range(len(newwordcloud["clouds"])):
                if newwordcloud["clouds"][i]["ts_start"] <= cur_time_span and cur_time_span <= newwordcloud["clouds"][i]["ts_end"]:
                    userSetlist[i].add(each[1])
    #print userSetlist
    talkmen = Set()
    for each in userSetlist:
        for eachone in each:
            talkmen.add(eachone)
    #print talkmen

    #print userSetlist
    for i in range(len(topics["topics"])):
        if len(userSetlist[i])>0:
            for eachUser in userSetlist[i]:
                user = {}
                user["name"] = eachUser
                topics["topics"][i]["users"].append(user)
        else:
            for eachUser in talkmen:
                user ={  }
                user["name"] = eachUser
                topics["topics"][i]["users"].append(user)

    for eachtopic in topics["topics"]:
        if len(eachtopic["users"]) >= len(talkmen)/2.0:
            eachtopic["color"] = "#FFF6BE"

def main():
    resultspath = "../results/pnas_tot/"
    tot_pickle_path = resultspath +"pnas_tot.pickle"
    tot_pickle = open(tot_pickle_path,"rb")
    par = pickle.load(tot_pickle)

    timefilepath = "../data/alltimes"
    timefile = open(timefilepath,"r")
    timelist = []
    for line in timefile:
        timelist.append(line.split()[1])

    #print timelist
    startTimePoint = timelist[0]
    endTimePoint = str(process.endtime)
    #print startTimePoint,endTimePoint

    xs,ys = getTimePoints(par["psi"])
    generateWordCloud(par['n'],par['word_token'],par['T'])
    #getTopicsTimeRange(par["psi"],ys,xs,int(endTimePoint)-int(startTimePoint))
    
    #generateTopics(wordcloud,startTimePoint,endTimePoint)
    #excute new wordclouds' ts_start & ts_end
    processWordCloud(par["psi"],ys,xs,int(endTimePoint)-int(startTimePoint))
    
    indexf = open("../data/index.txt","r")
    indexlist = list(indexf)
    index = indexlist[-1].split()[-1]

    generateNewTopics(startTimePoint,endTimePoint,index) 
    
    #output storyline
    talkmen = Set()
    for eachtopic in topics["topics"]:
        for eachuser in eachtopic["users"]:
            talkmen.add(eachuser["name"])
    #print talkmen
    #print int(endTimePoint),int(startTimePoint)
    #print newwordcloud
    #print topicsjson
    with open("../data/"+index+"/storyline.txt","w") as f:
        global timespan
        if timespan >= int(endTimePoint)-int(startTimePoint):
            timespan = int(endTimePoint)-int(startTimePoint)
            #print timespan
        for j in range(timespan):
            i =( int(endTimePoint)-int(startTimePoint) )*j/timespan
            eachtopicuser = Set()
            for eachtopic in topics["topics"]:
                if eachtopic["ts_start"]<=i and eachtopic["ts_end"]>=i:
                    for eachuser in eachtopic["users"]:
                        eachtopicuser.add(eachuser["name"])
            restmen = talkmen-eachtopicuser
            if len(eachtopicuser) !=0:
                if len(restmen) != 0:
                    string =",".join(eachtopicuser) + "\t"+"\t".join(restmen)+"\n"
                else:
                    string =",".join(eachtopicuser) + "\n"
                f.write(string)
            else:
                string ="\t".join(restmen)+"\n"
                f.write(string)
    
    if timespan == 3600:
        timelength = int(endTimePoint)-int(startTimePoint)
        for eachtopic in topics["topics"]:
            eachtopic["ts_start"] = eachtopic["ts_start"]*3600/timelength
            eachtopic["ts_end"] = eachtopic["ts_end"]*3600/timelength
        for eachcloud in newwordcloud["clouds"]:
            eachcloud["ts_start"] = eachcloud["ts_start"]*3600/timelength
            eachcloud["ts_end"] = eachcloud["ts_end"]*3600/timelength

    #clear keyword of clouds and topics
    for eachtopic in topics["topics"]:
        eachtopic["topic"] = " "
    for eachcloud in newwordcloud["clouds"]:
        eachcloud["topic"] = " "

    #output json
    wordcloudjson = json.dumps(newwordcloud)
    topicsjson = json.dumps(topics)
    with open("../data/"+index+"/wordcloud.json","w") as f1:
        f1.write(wordcloudjson)

    with open("../data/"+index+"/topic.json","w") as f2:
        f2.write(topicsjson)


if __name__ == "__main__":
    main()
