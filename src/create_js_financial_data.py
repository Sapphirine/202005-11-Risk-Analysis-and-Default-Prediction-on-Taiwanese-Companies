# -*- coding: utf-8 -*-
"""
Created on Thu May  7 00:25:31 2020

@author: Wayne
"""

import json
import os
import pathlib
import numpy as np

DATA_PATH = os.path.join(pathlib.Path(__file__).parent.parent, 'data/raw/fin_data')

with open(os.path.join(DATA_PATH, 'ratios2019Q3.json'), 'r', encoding='utf-8') as f:
    ratio = json.load(f)

keys = list(ratio['威盛'].keys())

a = list(ratio.values())
for i in range(len(a)):
    a[i] = list(a[i].values())

a = np.array(a)

for i in range(9):
    if i == 2 or i ==3:
        res = list(np.argsort(a[:,i]))
        for j in range(151):
            a[j,i] = res.index(j)
    else:
        res = list(np.argsort(-a[:,i]))
        for j in range(151):
            a[j,i] = res.index(j)

for i in range(151):
    for j in range(9):
        a[i,j] = 100 - a[i,j]/1.51

for i,k in enumerate(ratio):
    ratio[k] = [{'x':keys[ii], 'rank':v, 'value':round(ratio[k][keys[ii]],3)} for ii,v in enumerate(a[i])]

with open('js_fin.json', 'w', encoding='utf-8') as f:
    json.dump(ratio, f, ensure_ascii=False, indent=4)
        