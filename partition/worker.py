import refiner
import requester

import latex2mathml.converter
import pymongo

import Queue
import json
import threading
import sys

# for settings

try:
    con = pymongo.MongoClient("waps12b.iptime.org", 27017)
    # con = pymongo.MongoClient("slb-283692.ncloudslb.com", 27017)
    # con = pymongo.MongoClient("127.0.0.1", 30001)
except:
    print("<<< db connection error >>>")
    raise Exception # ServerSelectionTimeoutError

db = con.alan # db name
dbdata = db.page # collection name
dberr = db.errformula # collection name (for error)
core = 32
limit = 1

# function declaration

def getRawQ(_data):
    rawQ = Queue.Queue()
    for datum in _data:
        rawQ.put(datum)
    return rawQ

def doMakeJobQ(_id, _rawQ, _jobQ):

    task = 0
    tformula = 0

    while _rawQ.empty() == False:
        datum = _rawQ.get()
        url = datum["url"]
        title = datum["title"]
        formulas = datum["formulas"]
        # content = requester.getHtml(url)

        task = task + 1

        _fid = 0
        for formula in formulas:
            ltx = formula["latex"]
            mathml = formula["mathml"]
            element = {"url" : url, "title" : title, "ltx" : ltx, "mathml" : mathml, "content" : content, "_fid" : _fid}
            _jobQ.put(element)
            _fid = _fid + 1

            tformula = tformula + 1

    print("qworker (" + str(_id) + ") is has finished " + str(task) + " tasks(total " + str(tformula) + " formula(s))")

def doWork(_id, _jobQ):

    task = 0

    while _jobQ.empty() == False:
        datum = _jobQ.get()
        url = datum["url"]
        title = datum["title"]
        ltx = datum["ltx"]
        mathml = datum["mathml"]
        _fid = datum["_fid"]
        content = datum["content"]

        try:
            if content == "None": # request time out
                try:
                    dberr.insert({"url" : url, "title" : title, "ltx" : ltx, "_fid" : _fid})
                except:
                    continue
                continue
            requester.doPost(latex2mathml.converter.convert(refiner.handle(ltx)), title, url, content)
            requester.doPost(mathml, title, url, content)
        except:
            try:
                dberr.insert({"url" : url, "title" : title, "ltx" : ltx, "_fid" : _fid})
            except:
                continue

        task = task+1

# object declaration

class myQWorker (threading.Thread):
    def __init__(self, threadID, rawQ, jobQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.rawQ = rawQ
        self.jobQ = jobQ
    def run(self):
        doMakeJobQ(self.threadID, self.rawQ, self.jobQ)

class myJWorker (threading.Thread):
    def __init__(self, threadID, jobQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.jobQ = jobQ
    def run(self):
        doWork(self.threadID, self.jobQ)

# my logic

idx = 0

try:
    fp = open("index.dat", "r")
    idx = int(fp.readline())
    fp.close()
except:
    print("<<< no index file >>>")
    fp = open("index.dat", "w")
    fp.write(str(0))
    fp.close()

while idx < limit:
    # _id, formulas(latex), mathml, pageUrl(url), pageTitle(title), formulasNumber
    data = dbdata.find({"formulasNumber" : {"$gt" : 0}}).skip(idx*20).limit(20);

    rawQ = getRawQ(data)

    if rawQ.qsize() < 20:
        break

    jobQ = Queue.Queue()
    qworker = [myQWorker]*core

    for i in range(0, core):
        qworker[i] = myQWorker(i+1, rawQ, jobQ)
        qworker[i].start()

    while rawQ.empty() == False:
        continue

    for i in range(0, core):
        qworker[i].join()

    print("Job " + str(idx) + " is started")

    jworker = [myJWorker]*core
    for i in range(0, core):
        jworker[i] = myJWorker(i+1, jobQ)
        jworker[i].start()

    while jobQ.empty() == False:
        continue

    for i in range(0, core):
        jworker[i].join()

    print("Job " + str(idx) + " is finished")
    idx = idx + 1
    fp = open("index.dat", "w")
    fp.write(str(idx))
    fp.close()

con.close()
