# -*- coding: utf-8 -*-
"""
Created on Wed May  6 16:54:04 2020

@author: Wayne
"""
import json


with open('sentcount.json', 'r', encoding='utf-8') as f:
    sentcount = json.load(f)

mapp = {0:'Company News', 1:'Company PTT', 2:'CEO News', 3:'CEO PTT',4:'Industry News', 5:'Industry PTT', 6:'Product News', 7:'Product PTT',}

for comp in sentcount:
    data = []
    for i,a in enumerate(sentcount[comp]):
        start = -sum(a[:3])
        data.append({"n":mapp[i], "s":0, "start":-sum(a[:3]), "len":a[0]})
        data.append({"n":mapp[i], "s":1, "start":-sum(a[1:3]), "len":a[1]})
        data.append({"n":mapp[i], "s":2, "start":-sum(a[2:3]), "len":a[2]})
        data.append({"n":mapp[i], "s":3, "start":0, "len":a[3]})
        data.append({"n":mapp[i], "s":4, "start":a[3], "len":a[4]})
        data.append({"n":mapp[i], "s":5, "start":a[3]+a[4], "len":a[5]})
    sentcount[comp] = data

with open('js_sent.json', 'w', encoding='utf-8') as f:
    json.dump(sentcount, f, ensure_ascii=False, indent=4)