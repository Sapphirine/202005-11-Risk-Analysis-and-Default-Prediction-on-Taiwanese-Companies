# -*- coding: utf-8 -*-
"""
Created on Thu May  7 00:25:31 2020

@author: Wayne
"""

import json
import os

stocks = {}

for file in os.listdir('stock/'):
    with open(os.path.join('stock',file), 'r', encoding='utf-8') as f:
        new_data = []
        data = json.load(f)
        for d in data:
            new_data.append({'date':d, 'value':data[d]})
        stocks[file[:-5]] = new_data

with open('js_stock.json', 'w', encoding='utf-8') as f:
    json.dump(stocks, f, ensure_ascii=False, indent=4)