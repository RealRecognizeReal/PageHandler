import refiner
import json
import requests
import pymongo
import urllib
import latex2mathml.converter
import Queue
import threading
import sys
from bs4 import BeautifulSoup

def getHtml(pageUrl):
    try:
        fp = urllib.urlopen(pageUrl, timeout=5) # in 5 seconds
        raw = fp.read()
        fp.close()
        return BeautifulSoup(raw, "html.parser")
    except:
        return "None"
    return "None"

def doPost(_normalizedMathml, _pageTitle, _pageUrl, _content):
    url = "http://127.0.0.1:9200/engine/formula"
    _headers = {"content-type" : "application/json"}
    _data = {"nomarlizedMathml" : _normalizedMathml, "pageTitle" : _pageTitle, "pageUrl" : _pageUrl, "content" : _content}
    _data = json.dumps(_data);
    res = requests.post(url, data=_data, headers=_headers)
    return res.content

def getJobQ(_data):
    JobQ = Queue.Queue()
    for datum in _data:
        JobQ.put(datum)
    return JobQ

def doWork(_jobQ, _id):

    print("<<< worker (" + str(_id) + ") is started >>>")

    while _jobQ.empty() == False:
        datum = _jobQ.get()
        print(str(_id) + " allocated to " + str(datum["_id"]))
        url = datum["url"]
        title = datum["title"]
        formulas = datum["formulas"]
        content = getHtml(url)
        for formula in formulas:
            ltx = formula["latex"]
            try:
                ltx = refiner.handle(ltx)
                doPost(latex2mathml.converter.convert(ltx), title, url, content)
                doPost(formula["mathml"], title, url, content)
            except:
                try:
                    dberror.insert({"url" : url, "title" : title, "ltx" : formula["latex"]})
                except:
                    continue

    print("<<< worker (" + str(_id) + ") is finished completely >>")

class myWorker (threading.Thread):
    def __init__(self, threadID, jobQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.jobQ = jobQ
    def run(self):
        doWork(jobQ, self.threadID)

# for settings

try:
    con = pymongo.MongoClient("slb-283692.ncloudslb.com", 27017)
    # con = pymongo.MongoClient("127.0.0.1", 30001)
except:
    print("<<< db connection error >>>")
    sys.exit()


db = con.alan # db name
dbdata = db.page # collection name
dberror = db.errpage # collection name (for error)

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

while idx < 2:
    # _id, formulas(latex), mathml, pageUrl(url), pageTitle(title), formulasNumber
    data = dbdata.find({"formulasNumber" : {"$gt" : 0}}).skip(idx*40).limit(40);
    jobQ = getJobQ(data)

    worker1 = myWorker(1, jobQ)
    worker2 = myWorker(2, jobQ)
    worker3 = myWorker(3, jobQ)
    worker4 = myWorker(4, jobQ)
    worker5 = myWorker(5, jobQ)
    worker6 = myWorker(6, jobQ)

    worker1.start()
    worker2.start()
    worker3.start()
    worker4.start()
    worker5.start()
    worker6.start()

    while jobQ.empty() == False:
        continue

    idx = idx + 1
    fp = open("index.dat", "r")
    fp.write(str(idx))
    fp.close()

con.close()
