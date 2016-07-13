#coding=utf-8
import re
import time
import string

level = 111
endtime = None

def main():
    indexf = open("../data/index.txt","r")
    indexlist = list(indexf)
    index = indexlist[-1].split()[-1]
    #print index

    #index = "201604100002"
    f = open("../data/"+index+"/transcript.txt","rw")
    datastring = ""
    for line in f:
        datastring = datastring + line
    #delset = string.punctuation
    #datastring = line.translate(None,delset)
    puc = re.compile(r'[,.!?]')
    datastring = puc.sub(" ",datastring)
    #print datastring
    reg = r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)\t(.+?)\t(.+?)\n'
    data = re.compile(reg)
    datalist = data.findall(datastring)
    #print len(datalist)

    group = {}
    times = []
    timegroup = {}


    fa = open("../data/alltimes","w")
    fb = open("../data/alltitles","w")
    num = 0
    for each in datalist:
        timestr = time.strptime(each[0],"%Y-%m-%d %H:%M:%S")
        cur_time = int(time.mktime(timestr))
        times.append(cur_time)
        fb.write(each[2])
        fb.write("\n")

    times = sorted(times)
    mintime = times[0]
    maxtime = times[-1]
    global endtime
    endtime = maxtime
    print endtime
    for each in times:
        key = (each - mintime)/level
        if(not timegroup.has_key(key)):
            timegroup[key] = 1
        else:
            timegroup[key] += 1

    #print timegroup,len(timegroup)
    for key in timegroup:
        fa.write(str(timegroup[key])+"  ")
        fa.write(str(key*level+mintime)+"\n")

    fa.close()
    fb.close()

if __name__ == "__main__":
    main()
