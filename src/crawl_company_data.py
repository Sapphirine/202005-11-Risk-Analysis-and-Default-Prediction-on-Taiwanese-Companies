# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 14:28:02 2020

@author: Wayne
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import ast

res = requests.get("https://ic.tpex.org.tw/introduce.php?ic=F000", verify=False)

if res.status_code == 200:
    soup = BeautifulSoup(res.content, "html.parser")
    headline = soup.findAll("a", {"class": "company-text-over"})

company = {}
for h in headline:
    company[h.text] = h['href']

for c in company:
    if type(company[c]) == str and company[c][:5] == 'compa':
        i = 23
        res = requests.get("https://www.tpex.org.tw/storage/company_basic/company_basic.php?s=" + \
                           company[c][-4:] + "&m=" + str(i), verify=False)
        while res.content == b'':
            print(i)
            i -= 1
            res = requests.get("https://www.tpex.org.tw/storage/company_basic/company_basic.php?s=" + \
                           company[c][-4:] + "&m=" + str(i), verify=False)
        s = str(BeautifulSoup(res.content, "html.parser"))[16:-1]
        company[c] = ast.literal_eval(s)


#import pandas as pd
#a = pd.read_csv('company_data.csv').to_dict('records')
#
#for r in a:
#   if r['公司簡稱'] in company:
#       company[r['公司簡稱']] = r

import json

with open('company_data.json', 'w', encoding='utf-8') as f:
    json.dump(company, f, ensure_ascii=False, indent=4)