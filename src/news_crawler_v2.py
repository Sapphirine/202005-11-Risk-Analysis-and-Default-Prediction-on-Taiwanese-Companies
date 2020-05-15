# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 14:50:33 2020

@author: Wayne
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.parse import urlparse
import json
import os
import csv
import sys
import re
import urllib3
import time
import pathlib

RAW_DATA_PATH = os.path.join(pathlib.Path(__file__).parent.parent, 'data/raw')

# In some website, the article is not in <p>, so will be empty. Check articles 
# dictionary to delete empty news
file_name = 'company.txt'
#file_name = os.path.join(RAW_DATA_PATH, 'product.txt')
save_path = 'company_news'
is_list = True


search_period = {
        "Q1": "min%3A1%2F1%2F2019%2Ccd_max%3A3%2F31%2F2019&tbm=nws",
        "Q2": "min%3A4%2F1%2F2019%2Ccd_max%3A6%2F30%2F2019&tbm=nws",
        "Q3": "min%3A7%2F1%2F2019%2Ccd_max%3A9%2F30%2F2019&tbm=nws",
        "Q4": "min%3A10%2F1%2F2019%2Ccd_max%3A12%2F31%2F2019&tbm=nws",
        "Q5": "min%3A1%2F1%2F2020%2Ccd_max%3A3%2F31%2F2020&tbm=nws"
}

def is_crawled(name):
    files = os.listdir(save_path)
    if name+'.json' in files:
        return True
    return False

def read_list():
    print('Reading', file_name)
    word_list = []
    with open(file_name, encoding = 'utf8') as f:
        ff = f.read().splitlines()
    for line in ff:
        word_list.append(line.split(',')) 
    print('Total', len(word_list), 'lines')
    return word_list

def read_json():
    print('Reading', file_name)
    with open(file_name, encoding = 'utf8') as f:
        data = json.load(f)
    return data

def search(key_word="null", period=""):
    articles = {}

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    keyword = quote(key_word.encode('utf8'))
    print('duration = {0}'.format(search_period[period]))
   
    # Sample request in Google search 
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}# Sample request in Google search 
    # https://www.google.com/search?q=%E5%8F%B0%E7%A9%8D%E9%9B%BB&client=safari&rls=en&biw=1780&bih=946&source=lnt&tbs=cdr%3A1%2Ccd_min%3A7%2F1%2F2019%2Ccd_max%3A9%2F30%2F2019&tbm=nws
    res = requests.get("https://www.google.com/search?q=" + keyword + "&client=safari&rls=en&biw=1780&bih=946&source=lnt&tbs=cdr%3A1%2Ccd_" + search_period[period], headers = headers, verify=False)
    
    if res.status_code != 200:
        return articles

    url = []
    soup = BeautifulSoup(res.text, 'lxml')
    a = soup.find_all('a') 
    for i in a:
        k = i.get('href')
        #print(k)
        try:
            if k[:4] == 'http' and 'google' not in k:
                url.append(k)
        except:
            continue

    #print('total number of the news: {0}'.format(len(headline)))
    url = list(set(url))
    # Only iterate 100 posts
    for h in url:
        if len(articles) == 20:
            break
        try:
            resp = requests.get(h, allow_redirects=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
#            test = soup.findAll(text = re.compile(key_word))
#            
#            if len(test) == 0:
#                print('Keyword {0} not found in webpage {1}'.format(key_word, h))
#                continue
        except requests.ConnectionError as e:
            print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
            print(str(e))
            #renewIPadress()
            continue
        except requests.Timeout as e:
            print("OOPS!! Timeout Error")
            print(str(e))
            #renewIPadress()
            continue
        except requests.RequestException as e:
            print("OOPS!! General Error")
            print(str(e))
            #renewIPadress()
            continue
#        except KeyboardInterrupt:
#            print("Someone closed the program")

        # Concatenate all news together
        try:
            lines = soup.findAll('p')
            cont = ''
            for l in lines:
                cont += l.text
            head = soup.find('title')
            head = head.text.split('｜')[0].split('|')[0].split('-')[0]
            articles[head] = cont
        except:
            continue
#        print(cont)

    return articles

def save_data(articles, word, save_path):
    word = word.replace(" ", "_")
    word = word.replace("/", "")
    print('file name = {0}'.format(word))
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file = os.path.join(os.getcwd(),save_path, word + ".json")

    # save to json....
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

if __name__== "__main__":
#    word_list = read_list()
    print("This is news crawler")
    print('file = {0}, path = {1}'.format(file_name, save_path))
    if is_list:
        word_list = read_list()
        for words in word_list:
            name = words[0]
            if is_crawled(name):
                print(name, 'crawled, skipped.')
                continue
            articles = {"Q1":{}, "Q2":{}, "Q3":{}, "Q4":{}, "Q5":{}}
            for p in search_period:
                for word in words:
                    articles[p].update(search(word, p))
            save_data(articles, name, save_path)
    else:
        word_dic = read_json()
        for name in word_dic:
            if is_crawled(name):
                print(name, 'crawled, skipped.')
                continue
            articles = {"Q1":{}, "Q2":{}, "Q3":{}, "Q4":{}, "Q5":{}}
            for p in search_period:
                for word in word_dic[name]:
                    articles[p].update(search(word, p))
            save_data(articles, name, save_path)