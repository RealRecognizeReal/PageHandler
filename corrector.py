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
    # con = pymongo.MongoClient("127.0.0.1", 30001)
except:
    print("<<< db connection error >>>")
    raise Exception # ServerSelectionTimeoutError

db = con.alan # db name
dberr = db.errpage # collection name (for error)

# _id, formulas(latex), mathml, pageUrl(url), pageTitle(title), formulasNumber
data = dberr.find().limit(5);

success = 0
success2 = 0

for datum in data:
    _id = datum["_id"]
    title = datum["title"]
    url = datum["url"]
    if datum["type"] == "F":
        # formula
        ltx = datum["ltx"]
        _fid = datum["_fid"]
        try:
            rltx = refiner.prepare(ltx)
            requester.doFormulaPost(title, url, rltx)
            requester.doFormulaPost(title, url, refiner.convertLtxToMathml(rltx))
            dberr.remove({"_id" : _id})
            success = success + 1
        except:
            continue
    else:
        # page
        url = datum["url"]
        content = datum["content"]
        if content == "None":
            content = requester.getHtml(url)
            if content == "None":
                continue
        try:
            requester.doPagePost(title, url, content)
            dberr.remove({"_id" : _id})
            success2 = success2 + 1
        except:
            continue

con.close()

print("Success : " + str(success))
print("Success2 : " + str(success2))
