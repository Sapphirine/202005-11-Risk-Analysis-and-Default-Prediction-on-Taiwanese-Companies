# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 23:09:48 2020

@author: Wayne
"""

from graphdb import get_competitor, get_upstream, get_downstream
import json
import numpy as np
import os
import pathlib
import csv


RAW_DATA_PATH = os.path.join(pathlib.Path(__file__).parent.parent, 'data/raw')
CUR_PATH = os.path.dirname(__file__)

with open(os.path.join(RAW_DATA_PATH, 'company.txt'), 'r', encoding='utf-8') as f:
    company_list = f.read().splitlines()

ratio = []
with open(RAW_DATA_PATH + '\\fin_data\\ratios2018Q4.json', 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(RAW_DATA_PATH + '\\fin_data\\ratios2019Q1.json', 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(RAW_DATA_PATH + '\\fin_data\\ratios2019Q2.json', 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(RAW_DATA_PATH + '\\fin_data\\ratios2019Q3.json', 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(RAW_DATA_PATH + '\\fin_data\\ratios2019Q4.json', 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))

relation = {}
for c in company_list:
    relation[c+'_Q1'] = [2]*3
    relation[c+'_Q2'] = [2]*3
    relation[c+'_Q3'] = [2]*3
    relation[c+'_Q4'] = [2]*3
    relation[c+'_Q5'] = [2]*3

for c in company_list:
    comp = get_competitor(c)
    up = get_upstream(c)
    down = get_downstream(c)
    for i in range(5):
        compscore = []
        upscore = []
        downscore = []
        for cc in comp:
            try:
                compscore.append(ratio[i][cc]['z7'])
            except:
                continue
        for uu in up:
            try:
                upscore.append(ratio[i][cc]['z7'])
            except:
                continue
        for dd in down:
            try:
                downscore.append(ratio[i][cc]['z7'])
            except:
                continue
        if compscore:
            relation[c+'_Q'+str(i+1)][0] = np.average(compscore)
        if upscore:
            relation[c+'_Q'+str(i+1)][1] = np.average(upscore)
        if downscore:
            relation[c+'_Q'+str(i+1)][2] = np.average(downscore)
    print('Done', c)
        
with open('relation.json', 'w', encoding='utf-8') as f:
    json.dump(relation, f, ensure_ascii=False, indent=4)
