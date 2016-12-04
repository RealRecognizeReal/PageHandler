import refiner
import requester

import pymongo
import Queue
import json
import threading
import sys

# for db connection settings

try:
    con = pymongo.MongoClient("slb-283692.ncloudslb.com", 27017)
except:
    print("<<< db connection error >>>")
    raise Exception # ServerSelectionTimeoutError

db = con.alan # db name
dbdata = db.page # collection name
dberr = db.errpage # collection name (for error)
core = 16
limit = 700
dsize = 40

# function declaration

def getRawQ(_data):
    rawQ = Queue.Queue()
    for datum in _data:
        rawQ.put(datum)
    return rawQ

# object declaration

class myQWorker (threading.Thread):

    def __init__(self, threadID, rawQ, jobQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.rawQ = rawQ
        self.jobQ = jobQ

    def doWork(self, _id, _rawQ, _jobQ):

        while _rawQ.empty() == False:
            datum = _rawQ.get()
            url = datum["url"]
            title = datum["title"]
            formulas = datum["formulas"]
            _fid = 0
        
            for formula in formulas:
                ltx = formula["latex"]
                mathml = formula["mathml"]
                element = {"title" : title, "url" : url, "ltx" : ltx, "mathml" : mathml, "_fid" : _fid}
                _jobQ.put(element)
                _fid = _fid + 1

            content = requester.getHtml(url)
            try:
                requester.doPagePost(title, url, content)
            except:
                try:
                    dberr.insert({"title" : title, "url" : url, "content" : content, "type" : "P"})
                except:
                    continue

    def run(self):
        self.doWork(self.threadID, self.rawQ, self.jobQ)

class myJWorker (threading.Thread):

    def __init__(self, threadID, jobQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.jobQ = jobQ
   
    def doWork(self, _id, _jobQ):

        while _jobQ.empty() == False:
            datum = _jobQ.get()
            url = datum["url"]
            title = datum["title"]
            ltx = datum["ltx"]
            mathml = datum["mathml"]
            _fid = datum["_fid"]

            try:
                requester.doFormulaPost(title, url, ltx)
                requester.doFormulaPost(title, url, mathml)
                rltx = refiner.handle(ltx)
                requester.doFormulaPost(title, url, rltx)
                requester.doFormulaPost(title, url, refiner.convertLtxToMathml(rltx))
            except:
                try:
                    dberr.insert({"title" : title, "url" : url, "ltx" : ltx, "_fid" : _fid, "type" : "F"})
                except:
                    continue

    def run(self):
        self.doWork(self.threadID, self.jobQ)

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
    data = dbdata.find({"formulasNumber" : {"$gt" : 0}}).skip(idx*dsize).limit(dsize);

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
        if qworker[i].isAlive():
            qworker[i].join()

    print("Job " + str(idx) + " is started")

    jworker = [myJWorker]*core
    for i in range(0, core):
        jworker[i] = myJWorker(i+1, jobQ)
        jworker[i].start()

    while jobQ.empty() == False:
        continue

    for i in range(0, core):
        if jworker[i].isAlive():
            jworker[i].join()

    print("Job " + str(idx) + " is finished")
    idx = idx + 1
    fp = open("index.dat", "w")
    fp.write(str(idx))
    fp.close()

con.close()
