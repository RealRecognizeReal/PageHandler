import refiner
import json
import requests
import pymongo
import urllib
import latex2mathml.converter

def Post(_normalizedMathml, _pageTitle, _pageUrl):
    url = "http://127.0.0.1:9200/engine/formula"
    _headers = {"content-type" : "application/json"}
    _data = {"nomarlizedMathml" : _normalizedMathml, "pageTitle" : _pageTitle, "pageUrl" : _pageUrl}
    _data = json.dumps(_data);
    res = requests.post(url, data=_data, headers=_headers)
    #print(res.content);

con = pymongo.MongoClient("slb-283692.ncloudslb.com", 27017)
db = con.alan # db name
dbdata = db.page # collection name
dberror = db.errpage # collection name (for error)

idx = 0

try:
    fp = open('index.dat', 'r')
    idx = int(fp.readline())
    fp.close()
except IOError as e:
    print("index file is not exists")

# _id, formulas(latex), mathml, pageUrl(url), pageTitle(title)
data = dbdata.find({"formulasNumber" : {"$gt" : 0}}).skip(idx*50).limit(50); # x+1 ~ x+5

proceed = 0

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
            print("<<< error detected >>>")
            print(url + " + " + title + " + " + ltx)
            dberror.insert({"url" : url, "title" : title, "ltx" : formula["latex"]})
            print("<<< error information is sended to db >>>")
        Post(formula["mathml"], title, url)
        proceed = proceed + 1
        if proceed == 50:
            print("50 works are fininished completely")
            proceed = 0

if proceed > 0:
    print(str(proceed) + " works are finished complety")

idx = idx + 1
fp = open('index.dat', 'w')
fp.write(str(idx))
fp.close()
con.close()
