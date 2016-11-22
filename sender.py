import refiner
import json
import requests
import pymongo
import urllib2
import latex2mathml.converter
import Queue
import threading
import sys

# for settings

try:
    con = pymongo.MongoClient("slb-283692.ncloudslb.com", 27017)
    # con = pymongo.MongoClient("127.0.0.1", 30001)
except:
    print("<<< db connection error >>>")
    sys.exit()

db = con.alan # db name
dbdata = db.page # collection name
dberr = db.errformula # collection name (for error)
core = 10

# function declaration

def getHtml(pageUrl):
    try:
        fp = urllib2.urlopen(pageUrl, timeout=5)
        source = fp.read()
        fp.close()
        return source
    except:
        return "None"
    return "None"

def doPost(_normalizedMathml, _pageTitle, _pageUrl, _content):
    url = "http://127.0.0.1:9200/engine/formula"
    _headers = {"content-type" : "application/json"}
    _data = {"nomarlizedMathml" : _normalizedMathml, "pageTitle" : _pageTitle, "pageUrl" : _pageUrl, "content" : _content}
    _data = json.dumps(_data);
    res = requests.post(url, data=_data, headers=_headers)
    return res.status_code

def getRawQ(_data):
    rawQ = Queue.Queue()
    for datum in _data:
        rawQ.put(datum)
    return rawQ

def doMakeJobQ(_id, _rawQ, _jobQ):
    print("<<< qworker (" + str(_id) + ") is started >>>")

    while _rawQ.empty() == False:
        datum = _rawQ.get()
        print(str(_id) + " is processing with " + str(datum["_id"]))
        url = datum["url"]
        title = datum["title"]
        formulas = datum["formulas"]
        content = getHtml(url)
        _fid = 0
        for formula in formulas:
            ltx = formula["latex"]
            mathml = formula["mathml"]
            element = {"url" : url, "title" : title, "ltx" : ltx, "mathml" : mathml, "content" : content, "_fid" : _fid}
            _jobQ.put(element)
            _fid = _fid + 1
 
    print("<<< qworker (" + str(_id) + ") is finished >>>")

def doWork(_id, _jobQ):

    print("<<< jworker (" + str(_id) + ") is started >>>")

    while _jobQ.empty() == False:
        datum = _jobQ.get()
        url = datum["url"]
        title = datum["title"]
        ltx = datum["ltx"]
        mathml = datum["mathml"]
        _fid = datum["_fid"]
        content = datum["content"]

        try:
            doPost(latex2mathml.converter.convert(refiner.handle(ltx)), title, url, content)
            doPost(mathml, title, url, content)
        except:
            try:
                dberr.insert({"url" : url, "title" : title, "ltx" : ltx, "_fid" : _fid})
            except:
                continue

        print("<<<< jworker (" + str(_id) + ") has finished one task >>>>")

    print("<<< jworker (" + str(_id) + ") has finished completely >>")

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

while idx < 10:
    # _id, formulas(latex), mathml, pageUrl(url), pageTitle(title), formulasNumber
    data = dbdata.find({"formulasNumber" : {"$gt" : 0}}).skip(idx*40).limit(40);

    rawQ = getRawQ(data)
    jobQ = Queue.Queue()
    qworker = [myQWorker]*core

    print("<<< make job Q >>>")

    for i in range(0, core):
        qworker[i] = myQWorker(i+1, rawQ, jobQ)
        qworker[i].start()

    while rawQ.empty() == False:
        continue

    for i in range(0, core):
        qworker[i].join()

    print("<<< " + str(idx) + " Job is started")
 
    jworker = [myJWorker]*core
    for i in range(0, core):
        jworker[i] = myJWorker(i+1, jobQ)
        jworker[i].start()

    while jobQ.empty() == False:
       continue

    for i in range(0, core):
       jworker[i].join()

    print("<<< " + str(idx) + " Job is finished")
    idx = idx + 1
    fp = open("index.dat", "w")
    fp.write(str(idx))
    fp.close()

con.close()
