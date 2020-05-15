# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 19:07:06 2020

@author: Wayne
"""

import os
import json
import numpy as np
import pathlib

RAW_DATA_PATH = os.path.join(pathlib.Path(__file__).parent.parent, 'data/raw')

stock = []
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\stocks2018Q4.json'), 'r', encoding='utf-8') as f:
    stock.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\stocks2019Q1.json'), 'r', encoding='utf-8') as f:
    stock.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\stocks2019Q2.json'), 'r', encoding='utf-8') as f:
    stock.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\stocks2019Q3.json'), 'r', encoding='utf-8') as f:
    stock.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\stocks2019Q4.json'), 'r', encoding='utf-8') as f:
    stock.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\stocks2020Q1.json'), 'r', encoding='utf-8') as f:
    stock.append(json.load(f))    

ratio = []
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\ratios2018Q4.json'), 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\ratios2019Q1.json'), 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\ratios2019Q2.json'), 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\ratios2019Q3.json'), 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\ratios2019Q4.json'), 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))
with open(os.path.join(RAW_DATA_PATH, 'fin_data\\ratios2020Q1.json'), 'r', encoding='utf-8') as f:
    ratio.append(json.load(f))

with open(os.path.join(RAW_DATA_PATH, 'company.txt'), 'r', encoding='utf-8') as f:
    company_list = f.read().splitlines()
    
test = [v['z7'] for v in ratio[0].values()] + [v['z7'] for v in ratio[1].values()] +\
        [v['z7'] for v in ratio[2].values()] + [v['z7'] for v in ratio[3].values()] +\
        [v['z7'] for v in ratio[4].values()]
# max z7 is 4.956
# min z7 is 0.032

changes = []
for c in company_list:
    try:
        changes.append((float(stock[1][c])-float(stock[0][c]))/float(stock[0][c]))
    except:
        pass
    try:
        changes.append((float(stock[2][c])-float(stock[1][c]))/float(stock[1][c]))
    except:
        pass
    try:
        changes.append((float(stock[3][c])-float(stock[2][c]))/float(stock[2][c]))
    except:
        pass
    try:
        changes.append((float(stock[4][c])-float(stock[3][c]))/float(stock[3][c]))
    except:
        pass
    try:
        changes.append((float(stock[5][c])-float(stock[4][c]))/float(stock[4][c]))
    except:
        pass
# max stock change is 1.5
# min stock change is -0.66
        
label = {}      
for c in company_list:
    try:
        label[c+'_Q1'] = ratio[1][c]['z7'] + -2*(float(stock[1][c])-float(stock[0][c]))/float(stock[0][c]) + 3
    except:
        label[c+'_Q1'] = 'NA'
    try:
        label[c+'_Q2'] = ratio[2][c]['z7'] + -2*(float(stock[2][c])-float(stock[1][c]))/float(stock[1][c]) + 3
    except:
        label[c+'_Q2'] = 'NA'
    try:
        label[c+'_Q3'] = ratio[3][c]['z7'] + -2*(float(stock[3][c])-float(stock[2][c]))/float(stock[2][c]) + 3
    except:
        label[c+'_Q3'] = 'NA'
    try:
        label[c+'_Q4'] = ratio[4][c]['z7'] + -2*(float(stock[4][c])-float(stock[3][c]))/float(stock[3][c]) + 3
    except:
        label[c+'_Q4'] = 'NA'
    try:
        label[c+'_Q5'] = ratio[5][c]['z7'] + -2*(float(stock[5][c])-float(stock[4][c]))/float(stock[4][c]) + 3
    except:
        label[c+'_Q5'] = 'NA'

with open('label.json', 'w', encoding='utf-8') as f:
    json.dump(label, f, ensure_ascii=False, indent=4)