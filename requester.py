import json
import requests
import urllib2
import sys
import socket

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

def doFormulaPost(pageTitle, pageUrl, ltx, mathml):
    url = "http://my-ela:9200/engine/formula2"
    _headers = {"content-type" : "application/json"}
    _data = {"pageTitle" : pageTitle, "pageUrl" : pageUrl, "ltx" : ltx, "mathml" : mathml}
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

def getNormalizedLatex(rawLatex):
    rawLatex = rawLatex + "\n"
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(3)
    server_address = ("codingmonster.net", 2016)
    conn.connect(server_address)
    normalizedLatex = "err"
    try:
        conn.sendall(rawLatex)
        normalizedLatex = conn.recv(1000)
        if "err" in normalizedLatex:
            normalizedLatex = "err"
    except:
        normalizedLatex = "err" # network error (tcp)
    conn.close()
    return normalizedLatex
