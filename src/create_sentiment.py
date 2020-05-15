# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 05:49:33 2020

@author: Wayne
"""

import json
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pickle
import os
import pathlib
import csv

RAW_DATA_PATH = os.path.join(pathlib.Path(__file__).parent.parent, 'data/raw')
CUR_PATH = os.path.dirname(__file__)


forest = pickle.load(open(os.path.join(CUR_PATH, 'models/forest_all.sav'), 'rb'))
with open(os.path.join(RAW_DATA_PATH, 'company.txt'), 'r', encoding='utf-8') as f:
    company_list = f.read().splitlines()

sentiments = {}
for c in company_list:
    sentiments[c+'_Q1'] = [0]*8
    sentiments[c+'_Q2'] = [0]*8
    sentiments[c+'_Q3'] = [0]*8
    sentiments[c+'_Q4'] = [0]*8
    sentiments[c+'_Q5'] = [0]*8

sentcount = {}
for c in company_list:
    sentcount[c] = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],\
                      [0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]

model = SentenceTransformer('distiluse-base-multilingual-cased')

#################################################################
# COMPANY NEWS

files = os.listdir(os.path.join(RAW_DATA_PATH, 'company_news'))

for n in files:
    with open(os.path.join(RAW_DATA_PATH, 'company_news', n), 'r', encoding='utf-8') as f:
        a = json.load(f)
    for q in a:
        if a[q] != {}:
            emb = model.encode(list(a[q].values()))
            sent = forest.predict_proba(emb)
            sentiments[n[:-5]+'_'+q][0] = np.average(sent, axis = 0)[1]*2-1
            for s in sent:
                if s[1] < 0.167:
                    sentcount[n[:-5]][0][0] += 1
                elif s[1] < 0.333:
                    sentcount[n[:-5]][0][1] += 1
                elif s[1] < 0.5:
                    sentcount[n[:-5]][0][2] += 1
                elif s[1] < 0.667:
                    sentcount[n[:-5]][0][3] += 1
                elif s[1] < 0.833:
                    sentcount[n[:-5]][0][4] += 1
                else:
                    sentcount[n[:-5]][0][5] += 1

print('Done company news')

#################################################################
# COMPANY PTT

files = os.listdir(os.path.join(RAW_DATA_PATH, 'company_ptt'))

for n in files:
    with open(os.path.join(RAW_DATA_PATH, 'company_ptt', n), 'r', encoding='utf-8') as f:
        a = json.load(f)
    if a == []:
        continue
    Q1 = []
    Q2 = []
    Q3 = []
    Q4 = []
    Q5 = []
    for post in a:
        try:
            content = model.encode([post['content']])
            comment = model.encode([c['text'] for c in post['comment']])
        except:
            content = model.encode([post['title']]) # use title if no content
        try: # comment could be empty
            if post['date'] <= '2019/03/31':
                Q1.append(forest.predict_proba(content)[0][1]*2-1)
                Q1.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/06/30':
                Q2.append(forest.predict_proba(content)[0][1]*2-1)
                Q2.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/09/30':
                Q3.append(forest.predict_proba(content)[0][1]*2-1)
                Q3.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/12/31':
                Q4.append(forest.predict_proba(content)[0][1]*2-1)
                Q4.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2020/03/31':
                Q5.append(forest.predict_proba(content)[0][1]*2-1)
                Q5.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
        except:
            pass
    if Q1:
        sentiments[n[4:-5]+'_Q1'][1] = np.average(Q1)
    if Q2:
        sentiments[n[4:-5]+'_Q2'][1] = np.average(Q2)
    if Q3:
        sentiments[n[4:-5]+'_Q3'][1] = np.average(Q3)
    if Q4:
        sentiments[n[4:-5]+'_Q4'][1] = np.average(Q4)
    if Q5:
        sentiments[n[4:-5]+'_Q5'][1] = np.average(Q5)

    for s in Q1+Q2+Q3+Q4+Q5:
        if s < -0.667:
            sentcount[n[4:-5]][1][0] += 1
        elif s < -0.333:
            sentcount[n[4:-5]][1][1] += 1
        elif s < 0:
            sentcount[n[4:-5]][1][2] += 1
        elif s < 0.333:
            sentcount[n[4:-5]][1][3] += 1
        elif s < 0.667:
            sentcount[n[4:-5]][1][4] += 1
        else:
            sentcount[n[4:-5]][1][5] += 1
            
print('Done company ptt')

#################################################################
# PRESIDENT NEWS

files = os.listdir(os.path.join(RAW_DATA_PATH, 'president_news'))

for n in files:
    with open(os.path.join(RAW_DATA_PATH, 'president_news', n), 'r', encoding='utf-8') as f:
        a = json.load(f)
    for q in a:
        if a[q] != {}:
            emb = model.encode(list(a[q].values()))
            sent = forest.predict_proba(emb)
            sentiments[n[:-5]+'_'+q][2] = np.average(sent, axis = 0)[1]*2-1
            for s in sent:
                if s[1] < 0.167:
                    sentcount[n[:-5]][2][0] += 1
                elif s[1] < 0.333:
                    sentcount[n[:-5]][2][1] += 1
                elif s[1] < 0.5:
                    sentcount[n[:-5]][2][2] += 1
                elif s[1] < 0.667:
                    sentcount[n[:-5]][2][3] += 1
                elif s[1] < 0.833:
                    sentcount[n[:-5]][2][4] += 1
                else:
                    sentcount[n[:-5]][2][5] += 1

print('Done president news')

#################################################################
# PRESIDENT PTT

files = os.listdir(os.path.join(RAW_DATA_PATH, 'president_ptt'))
sent_list = {}

for n in files:
    with open(os.path.join(RAW_DATA_PATH, 'president_ptt', n), 'r', encoding='utf-8') as f:
        a = json.load(f)
    if a == []:
        continue
    Q1 = []
    Q2 = []
    Q3 = []
    Q4 = []
    Q5 = []
    for post in a:
        try:
            content = model.encode([post['content']])
            comment = model.encode([c['text'] for c in post['comment']])
        except:
            content = model.encode([post['title']]) # use title if no content
        try: # comment could be empty
            if post['date'] <= '2019/03/31':
                Q1.append(forest.predict_proba(content)[0][1]*2-1)
                Q1.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/06/30':
                Q2.append(forest.predict_proba(content)[0][1]*2-1)
                Q2.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/09/30':
                Q3.append(forest.predict_proba(content)[0][1]*2-1)
                Q3.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/12/31':
                Q4.append(forest.predict_proba(content)[0][1]*2-1)
                Q4.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2020/03/31':
                Q5.append(forest.predict_proba(content)[0][1]*2-1)
                Q5.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
        except:
            pass
    if Q1:
        sentiments[n[4:-5]+'_Q1'][3] = np.average(Q1)
    if Q2:
        sentiments[n[4:-5]+'_Q2'][3] = np.average(Q2)
    if Q3:
        sentiments[n[4:-5]+'_Q3'][3] = np.average(Q3)
    if Q4:
        sentiments[n[4:-5]+'_Q4'][3] = np.average(Q4)
    if Q5:
        sentiments[n[4:-5]+'_Q5'][3] = np.average(Q5)
    
    for s in Q1+Q2+Q3+Q4+Q5:
        if s < -0.667:
            sentcount[n[4:-5]][3][0] += 1
        elif s < -0.333:
            sentcount[n[4:-5]][3][1] += 1
        elif s < 0:
            sentcount[n[4:-5]][3][2] += 1
        elif s < 0.333:
            sentcount[n[4:-5]][3][3] += 1
        elif s < 0.667:
            sentcount[n[4:-5]][3][4] += 1
        else:
            sentcount[n[4:-5]][3][5] += 1
    
print('Done president ptt')

#################################################################
# INDUSTRY NEWS

files = os.listdir(os.path.join(RAW_DATA_PATH, 'industry_news'))
sent_list = {}

for n in files:
    with open(os.path.join(RAW_DATA_PATH, 'industry_news', n), 'r', encoding='utf-8') as f:
        a = json.load(f)
    for q in a:
        emb = model.encode(list(a[q].values()))
        sent = forest.predict_proba(emb)
        for s in sent:
            if s[1] < 0.167:
                i = 0
            elif s[1] < 0.333:
                i = 1
            elif s[1] < 0.5:
                i = 2
            elif s[1] < 0.667:
                i = 3
            elif s[1] < 0.833:
                i = 4
            else:
                i = 5
            for c in company_list:
                sentcount[c][4][i] += 1
        sent_list[n[:-5]+'_'+q] = np.average(sent, axis = 0)[1]*2-1

# Since all companies belong to same industry in our case
for comp in sentiments:
    sentiments[comp][4] = sent_list[n[:-5]+comp[-3:]]

print('Done industry news')

#################################################################
# INDUSTRY PTT

files = os.listdir(os.path.join(RAW_DATA_PATH, 'industry_ptt'))
sent_list = {}

for n in files:
    with open(os.path.join(RAW_DATA_PATH, 'industry_ptt', n), 'r', encoding='utf-8') as f:
        a = json.load(f)
    if a == []:
        continue
    Q1 = []
    Q2 = []
    Q3 = []
    Q4 = []
    Q5 = []
    for post in a:
        try:
            content = model.encode([post['content']])
            comment = model.encode([c['text'] for c in post['comment']])
        except:
            content = model.encode([post['title']]) # use title if no content
        try: # comment could be empty
            if post['date'] <= '2019/03/31':
                Q1.append(forest.predict_proba(content)[0][1]*2-1)
                Q1.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/06/30':
                Q2.append(forest.predict_proba(content)[0][1]*2-1)
                Q2.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/09/30':
                Q3.append(forest.predict_proba(content)[0][1]*2-1)
                Q3.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/12/31':
                Q4.append(forest.predict_proba(content)[0][1]*2-1)
                Q4.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2020/03/31':
                Q5.append(forest.predict_proba(content)[0][1]*2-1)
                Q5.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
        except:
            pass
    if Q1:
        sent_list[n[4:-5]+'_Q1'] = np.average(Q1)
    if Q2:
        sent_list[n[4:-5]+'_Q2'] = np.average(Q2)
    if Q3:
        sent_list[n[4:-5]+'_Q3'] = np.average(Q3)
    if Q4:
        sent_list[n[4:-5]+'_Q4'] = np.average(Q4)
    if Q5:
        sent_list[n[4:-5]+'_Q5'] = np.average(Q5)

# calculate sentcount
for s in Q1+Q2+Q3+Q4+Q5:
    if s < -0.667:
        i = 0
    elif s < -0.333:
        i = 1
    elif s < 0:
        i = 2
    elif s < 0.333:
        i = 3
    elif s < 0.667:
        i = 4
    else:
        i = 5
    for c in company_list:
        sentcount[c][5][i] += 1
            
# Since all companies belong to same industry in our case
for comp in sentiments:
    try: # could be empty for sent_list
        sentiments[comp][5] = sent_list[n[4:-5]+comp[-3:]]
    except:
        pass

print('Done industry ptt')

#################################################################
# PRODUCT NEWS

files = os.listdir(os.path.join(RAW_DATA_PATH, 'product_news'))
sent_list = {}
sents_list = {}

for n in files:
    with open(os.path.join(RAW_DATA_PATH, 'product_news', n), 'r', encoding='utf-8') as f:
        a = json.load(f)
    sents_list[n[:-5]] = []
    for q in a:
        emb = model.encode(list(a[q].values()))
        sent = forest.predict_proba(emb)
        sents_list[n[:-5]] += list(sent)
        sent_list[n[:-5]+'_'+q] = np.average(sent, axis = 0)[1]*2-1

# read relationship and generate company product dictionary
with open(os.path.join(RAW_DATA_PATH, 'Relationship.csv'), 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    relations = list(csv_reader)
    
comp_prod = {}

for r in relations:
    if r[1] =='公司':
        if r[0] not in comp_prod:
            comp_prod[r[0]] = [r[3]]
        else:
            comp_prod[r[0]].append(r[3])

# Calculate average sentiment score for all products
for comp in sentiments:
    sents = []
    try: # probably not in comp_prod
        for p in comp_prod[comp[:-3]]:
            if len(p.split('、')) > 1:
                for pp in p.split('、'):
                    sents.append(sent_list[pp+comp[-3:]])
            elif len(p.split('/')) > 1:
                for pp in p.split('/'):
                    sents.append(sent_list[pp+comp[-3:]])
            else:
                sents.append(sent_list[p+comp[-3:]])
    except:
        pass
    if sents:
        sentiments[comp][6] = np.average(sents)

# process sents_list
for prod in sents_list:
    for i,s in enumerate(sents_list[prod]):
        if s[1] < 0.167:
            sents_list[prod][i] = 0
        elif s[1] < 0.333:
            sents_list[prod][i] = 1
        elif s[1] < 0.5:
            sents_list[prod][i] = 2
        elif s[1] < 0.667:
            sents_list[prod][i] = 3
        elif s[1] < 0.833:
            sents_list[prod][i] = 4
        else:
            sents_list[prod][i] = 5
            
# calculate sentcount
for comp in sentcount:
    try: 
        for p in comp_prod[comp]:
            if len(p.split('、')) > 1:
                for pp in p.split('、'):
                    for i in sents_list[pp]:
                        sentcount[comp][6][i] += 1
            elif len(p.split('/')) > 1:
                for pp in p.split('/'):
                    for i in sents_list[pp]:
                        sentcount[comp][6][i] += 1
            else:
                for i in sents_list[p]:
                    sentcount[comp][6][i] += 1
        for i, a in enumerate(sentcount[comp][6]):
            sentcount[comp][6][i] = int(sentcount[comp][6][i]/len(comp_prod[comp])) + 1
    except:
        pass
    

print('Done product news')

#################################################################
# PRODUCT PTT

files = os.listdir(os.path.join(RAW_DATA_PATH, 'product_ptt'))
sent_list = {}
sents_list = {}

for n in files:
    with open(os.path.join(RAW_DATA_PATH, 'product_ptt', n), 'r', encoding='utf-8') as f:
        a = json.load(f)
    if a == []:
        continue
    Q1 = []
    Q2 = []
    Q3 = []
    Q4 = []
    Q5 = []
    for post in a:
        try:
            content = model.encode([post['content']])
            comment = model.encode([c['text'] for c in post['comment']])
        except:
            content = model.encode([post['title']]) # use title if no content
        try: # comment could be empty
            if post['date'] <= '2019/03/31':
                Q1.append(forest.predict_proba(content)[0][1]*2-1)
                Q1.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/06/30':
                Q2.append(forest.predict_proba(content)[0][1]*2-1)
                Q2.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/09/30':
                Q3.append(forest.predict_proba(content)[0][1]*2-1)
                Q3.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2019/12/31':
                Q4.append(forest.predict_proba(content)[0][1]*2-1)
                Q4.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
            elif post['date'] <= '2020/03/31':
                Q5.append(forest.predict_proba(content)[0][1]*2-1)
                Q5.append(np.average(forest.predict_proba(comment),axis=0)[1]*2-1)
        except:
            pass
    if Q1:
        sent_list[n[4:-5]+'_Q1'] = np.average(Q1)
    if Q2:
        sent_list[n[4:-5]+'_Q2'] = np.average(Q2)
    if Q3:
        sent_list[n[4:-5]+'_Q3'] = np.average(Q3)
    if Q4:
        sent_list[n[4:-5]+'_Q4'] = np.average(Q4)
    if Q5:
        sent_list[n[4:-5]+'_Q5'] = np.average(Q5)
    
    for s in Q1+Q2+Q3+Q4+Q5:
        if s < -0.667:
            i = 0
        elif s < -0.333:
            i = 1
        elif s < 0:
            i = 2
        elif s < 0.333:
            i = 3
        elif s < 0.667:
            i = 4
        else:
            i = 5
        try:
            sents_list[n[4:-5]].append(i)
        except:
            sents_list[n[4:-5]] = [i]

# Reuse the product dict
for comp in sentiments:
    sents = []
    try:
        for p in comp_prod[comp[:-3]]:
            if len(p.split('、')) > 1:
                for pp in p.split('、'):
                    try: # could have no product ptt in sent_list
                        sents.append(sent_list[pp+comp[-3:]])
                    except:
                        pass
            elif len(p.split('/')) > 1:
                for pp in p.split('/'):
                    try: # could have no product ptt in sent_list
                        sents.append(sent_list[pp+comp[-3:]])
                    except:
                        pass
            else:
                try: # could have no product ptt in sent_list
                    sents.append(sent_list[p+comp[-3:]])
                except:
                    pass
    except:
        pass
    if sents:
        sentiments[comp][7] = np.average(sents)
    
# calculate sentcount
for comp in sentcount:
    try: 
        for p in comp_prod[comp]:
            if len(p.split('、')) > 1:
                for pp in p.split('、'):
                    for i in sents_list[pp]:
                        sentcount[comp][7][i] += 1
            elif len(p.split('/')) > 1:
                for pp in p.split('/'):
                    for i in sents_list[pp]:
                        sentcount[comp][7][i] += 1
            else:
                for i in sents_list[p]:
                    sentcount[comp][7][i] += 1
        for i, a in enumerate(sentcount[comp][7]):
            sentcount[comp][7][i] = int(sentcount[comp][7][i]/len(comp_prod[comp])) + 1
    except:
        pass


print('Done product ptt')

# write into json file
with open('sentiment.json', 'w', encoding='utf-8') as f:
    json.dump(sentiments, f, ensure_ascii=False, indent=4)

with open('sentcount.json', 'w', encoding='utf-8') as f:
    json.dump(sentcount, f, ensure_ascii=False, indent=4)
