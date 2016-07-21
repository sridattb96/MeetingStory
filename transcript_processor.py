#!/usr/bin/python

import csv
import json
import sys
import time 
import os.path

from collections import Counter

MAX_THICKNESS = 16
MIN_THICKNESS = 2

# with open('./project/data/codeDic.txt', 'r') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         arr = row[0].split('\t')
#         code_d[arr[0]] = arr[1]

# helper functions
def toSeconds(time):
    time_arr = time.split(":")
    return int(time_arr[0])*3600 + int(time_arr[1])*60 + int(time_arr[2])

def populateWordsDict(dirname, initial_time, start_times, end_times):
    word_d = [None] * len(end_times)

    with open(dirname + '/transcript.txt', 'r') as f:
        reader = csv.reader(f)
        i = 0;
        for row in reader:

            # print len(start_times)
            if i == len(end_times):
                break;

            # get elements in row
            row = ', '.join(row) + ''
            arr = row.split('\t')
            time = arr[0].split(" ")
            name = arr[1]
            content = arr[2].split(" ")

            if (toSeconds(time[1]) - initial_time) >= start_times[i]:
                # print '{}'.format(name)
                if word_d[i] != None:
                    if name in word_d[i]:
                        word_d[i][name] += len(content);
                    else:
                        word_d[i][name] = len(content);
                else: 
                    word_d[i] = {};
                    word_d[i][name] = len(content)

            if int(toSeconds(time[1]) - initial_time) >= int(end_times[i]):
                i = i + 1

    return word_d

def findThickness(arr, word_d, start_time, end_time):
    wordcmax = word_d[max(word_d, key=lambda i: word_d[i])]
    wordcmin = word_d[min(word_d, key=lambda i: word_d[i])]

    for k in word_d:
        users = {}
        users["name"] = k
        
        tempObj = {};
        if wordcmax - wordcmin != 0:
            ratio = float(abs(word_d[k] - wordcmin))/(wordcmax - wordcmin)
        else:
            ratio = 0
        num = (MAX_THICKNESS - MIN_THICKNESS)*ratio + MIN_THICKNESS;
        num = 2*round(num/2);
        tempObj["t"] = num;
        tempObj["ts_start"] = start_time;
        tempObj["ts_end"] = end_time;
        users["thickness"] = tempObj;

        # users["color"] = code_d[k]
        arr.append(users)

def createJsonObject(word_counts, start_times, end_times):
    arr = []
    for x in range(0, len(start_times)):
        findThickness(arr, word_counts[x], start_times[x], end_times[x]);

    return arr;

def rearrange(users_arr):
    user_json = {};
    for x in range(0, len(users_arr)):
        name = users_arr[x]["name"];
        thickness = users_arr[x]["thickness"];
        if name in user_json:
            user_json[name].append(thickness);
        else:
            user_json[name] = [];
            user_json[name].append(thickness);

    obj = {};
    obj["users"] = [];
    for key in user_json:
        user = {};
        user["name"] = key
        user["thickness"] = user_json[key];
        # user["color"] = code_d[key];
        obj["users"].append(user);

    return obj

def addGapThickness(final_json, start_times, end_times):

    for x in range(0, len(final_json["users"])):
        temp = [];
        for i in range(0, len(start_times)):
            obj = {};
            obj["t"] = 1.0
            obj["ts_start"] = start_times[i];
            obj["ts_end"] = end_times[i];
            temp.append(obj)
        for y in range(0, len(final_json["users"][x]["thickness"])):
            s1 = final_json["users"][x]["thickness"][y]["ts_start"];
            temp[start_times.index(s1)] = final_json["users"][x]["thickness"][y];
        final_json["users"][x]["thickness"] = temp;

    return final_json

def addColors(dirname, final_json):
    colors = [line.rstrip('\n') for line in open(dirname + '/../colors.txt')]
    
    for x in range(0, len(final_json["users"])):
        final_json["users"][x]["color"] = colors[x];

    return final_json

# main script

# get start and end times
def get_start_end_times(dirname):
    times = {}
    times["start"] = []
    times["end"] = []

    if os.path.exists(dirname + '/topic.json'):
        with open(dirname + '/topic.json', 'r') as data_file:    
            data = json.load(data_file)
            for obj in data["topics"]:
                # start_times.append(obj["ts_start"])
                # end_times.append(obj["ts_end"])
                times["start"].append(obj["ts_start"])
                times["end"].append(obj["ts_end"])
    else:
        print "no topic.json"
        exit()

    return times


# populate word_dictionary
def get_user_contribution(dirname):

    times = get_start_end_times(dirname)
    start_times = times["start"]
    end_times = times["end"]

    with open(dirname + '/transcript.txt', 'r') as f:
        reader = csv.reader(f)
        fileStartTime = 0;

        for row in reader:
            row = ', '.join(row) + ''
            arr = row.split('\t')
            time_ele = arr[0].split(" ")
            name = arr[1]
            content = arr[2]
            fileStartTime = toSeconds(time_ele[1])
            break

        word_counts = populateWordsDict(dirname, fileStartTime, start_times, end_times);
        users_arr = createJsonObject(word_counts, start_times, end_times);
        
        final_json = rearrange(users_arr);
        final_json = addGapThickness(final_json, start_times, end_times);
        final_json = addColors(dirname, final_json);

    # save data to json file
    with open(dirname + '/user.json', 'w') as f:
        json.dump(final_json, f)

