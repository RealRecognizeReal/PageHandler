import json
import requests
import urllib2
import sys

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

def doFormulaPost(pageTitle, pageUrl, normalizedMathml):
    url = "http://my-ela:9200/engine/formula"
    _headers = {"content-type" : "application/json"}
    _data = {"pageTitle" : pageTitle, "pageUrl" : pageUrl, "normalizedMathml" : normalizedMathml}
    _data = json.dumps(_data);
    res = requests.post(url, data=_data, headers=_headers)
    return res.status_code

def doPagePost(pageTitle, pageUrl, content):
    url = "http://my-ela:9200/engine/page" # 127.0.0.1 (local)
    _headers = {"content-type" : "application/json"}
    _data = {"pageTitle" : pageTitle, "pageUrl" : pageUrl, "content" : content}
    _data = json.dumps(_data);
    res = requests.post(url, data=_data, headers=_headers)
    return res.status_code
