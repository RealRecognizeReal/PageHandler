import refiner
import requester

import latex2mathml.converter
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

data = dberr.find()
fp = open("errpage.out", "w")

for datum in data:
    title = datum["title"]
    if datum["type"] == "F":
        # formula
        try:
            ltx = datum["ltx"]
            fp.write(ltx+'\n')
        except:
            print("err !!!")
    else:
        continue

fp.close()
con.close()
