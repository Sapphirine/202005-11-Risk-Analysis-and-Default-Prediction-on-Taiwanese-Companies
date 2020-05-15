# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 17:13:20 2020

@author: Wayne
"""
import requests
import numpy as np
import json
import time

dates = ['20181001', '20181101','20181201','20190101','20190201','20190301',\
         '20190401','20190501','20190601','20190701','20190801','20190901',\
         '20191001','20191101','20191201']


with open('company_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = {}

for d in data:
    if "COMPANY_ID" in data[d]:
        stock = []
        for date in dates:
            url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date='+\
                    date + '&stockNo=' + data[d]["COMPANY_ID"]
            r = requests.get(url)
            time.sleep(5)
            try:
                stock += [[i[0],i[6]] for i in r.json()['data']]
            except:
                break
    stocks[d] = stock


with open('stock.json', 'w', encoding='utf-8') as f:
    json.dump(stocks, f, ensure_ascii=False, indent=4)

#stock = []
#for date in dates:
#    url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date='+\
#            date+'&stockNo=' + '2388'
#    r = requests.get(url)
#    stock += [[i[0],i[6]] for i in r.json()['data']]