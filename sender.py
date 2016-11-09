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
    print(res.content);

con = pymongo.MongoClient("slb-283692.ncloudslb.com", 27017)

db = con.alan # db name
db.create_collection("index", 
dbdata = db.page # collection name
idx = db.index.find()["idx"]

# _id, formulas(latex), mathml, pageUrl(url), pageTitle(title)
data = dbdata.find().skip(idx*5).limit(5); # x+1 ~ x+5

for datum in data:
    url = datum["url"]
    title = datum["title"]
    formulars = datum["formulas"]
    for formular in formulars:
        ltx = formular["latex"]
        ltx = refiner.handle(ltx)
        Post(latex2mathml.converter.convert(ltx), title, url)
        Post(formular["mathml"], title, url)

db.index.find
con.close()
