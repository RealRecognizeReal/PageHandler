import refiner
import json
import requests
import pymongo
import urllib
import latex2mathml.converter

import sys

def Post(_normalizedMathml, _pageTitle, _pageUrl):
    url = "http://127.0.0.1:9200/engine/formula"
    _headers = {"content-type" : "application/json"}
    _data = {"nomarlizedMathml" : _normalizedMathml, "pageTitle" : _pageTitle, "pageUrl" : _pageUrl}
    _data = json.dumps(_data);
    res = requests.post(url, data=_data, headers=_headers)
    #print(res.content);

try:
    con = pymongo.MongoClient("slb-283692.ncloudslb.com", 27017)
except:
    print("<<< db connection error >>>")
    sys.exit()

db = con.alan # db name
dbdata = db.page # collection name
dberror = db.errpage # collection name (for error)

idx = 0

try:
    fp = open('index.dat', 'r')
    idx = int(fp.readline())
    fp.close()
except:
    print("index file is not exists")

# _id, formulas(latex), mathml, pageUrl(url), pageTitle(title), formulasNumber
data = dbdata.find({"formulasNumber" : {"$gt" : 0}}).skip(idx*10000).limit(10000); # x+1 ~ x+5

totalFormulas = 0
totalError = 0

for datum in data:
    totalFormulas = totalFormulas + datum["formulasNumber"]

chk = [0]*101

proceed = 0
data = dbdata.find({"formulasNumber" : {"$gt" : 0}}).skip(idx*10000).limit(10000); # x+1 ~ x+5

print("<<< works are started >>>")

for datum in data:
    url = datum["url"]
    title = datum["title"]
    formulas = datum["formulas"]
    for formula in formulas:
        ltx = formula["latex"]
        ltx = refiner.handle(ltx)
        try:
            Post(latex2mathml.converter.convert(ltx), title, url)
        except:
            totalError = totalError + 1
            try:
                dberror.insert({"url" : url, "title" : title, "ltx" : formula["latex"]})
                #print("<<< error detected >>>")
                #print(url + " + " + title + " + " + ltx)
                #print("<<< error information is sended to db >>>")
            except:
                #print("<<< duplicated error info and skipped >>>")
                proceed = proceed+1
                proceed = proceed-1
        try:
            Post(formula["mathml"], title, url)
            proceed = proceed + 1
            percentage = proceed*100/totalFormulas
            if chk[percentage] == 0:
                chk[percentage] = 1
                print(str(percentage) + "%")
        except:
            proceed = proceed+1
            proceed = proceed-1


print("<<< works are finished completely >>")
print("<<< " + str(totalError) + " errors / " + str(totalFormulas) + " formulas >>>")

idx = idx + 1
fp = open('index.dat', 'w')
fp.write(str(idx))
fp.close()
con.close()
