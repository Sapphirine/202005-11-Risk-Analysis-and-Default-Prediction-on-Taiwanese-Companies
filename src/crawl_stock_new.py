# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 23:52:55 2020

@author: Wayne
"""

import requests
import json
import time

d1 = '2018/10/01'
d2 = '2020/05/01'

def get_dates_id(data):
    i1 = 0
    i2 = len(data[0])-1
    for i in range(len(data[0])):
        if data[0][i] >= d1:
            i1 = i
            break
    
    for i in range(len(data[0])):
        if data[0][i] > d2:
            i2 = i-1
            break
    return i1, i2


with open('company_data.json', 'r', encoding='utf-8') as f:
    compdata = json.load(f)

for d in compdata:
    if "COMPANY_ID" in compdata[d]:
        r = requests.get('https://jdata.yuanta.com.tw/Z/ZC/ZCW/CZKC1.djbcd?a=' +\
                         compdata[d]["COMPANY_ID"] + '&b=D&c=1440')
        data = r.text.split()
        try:
            data = [data[0].split(','), data[4].split(',')]
        except:
            print('No data on', d)
            continue
        i1, i2 = get_dates_id(data)
        stocks = {}
        try:
            for i in range(i1,i2+1):
                stocks[data[0][i]] = data[1][i]
        except:
            print('Date ranges wrong')
            break
        with open('stock/' + d + '.json', 'w', encoding='utf-8') as f:
            json.dump(stocks, f, ensure_ascii=False, indent=4)
        print('Done', d)
    else:
        print('Skipped', d)
    time.sleep(2)
    

