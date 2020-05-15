#
# This file is used to retrieve posts from Google news.
# Usage:
# python news_crawler.py ${CSV_FILE} ${DEST_FOLDER}
#
# Example:
# python news_crawler.py computer_peripherals.csv ./global_industry/
#
#

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
import certifi

# In some website, the article is not in <p>, so will be empty. Check articles 
# dictionary to delete empty news

skip_list = ['電腦及周邊設備', '上游', '下游']

search_period = {
        "Q1": "min%3A1%2F1%2F2019%2Ccd_max%3A3%2F31%2F2019&tbm=nws",
        "Q2": "min%3A4%2F1%2F2019%2Ccd_max%3A6%2F30%2F2019&tbm=nws",
        "Q3": "min%3A7%2F1%2F2019%2Ccd_max%3A9%2F30%2F2019&tbm=nws",
        "Q4": "min%3A10%2F1%2F2019%2Ccd_max%3A9%2F31%2F2019&tbm=nws",
        "Q5": "min%3A1%2F1%2F2020%2Ccd_max%3A3%2F31%2F2020&tbm=nws"
}

def search(key_word="null", period=""):
    articles = {}

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if key_word == "null" or key_word in skip_list:
        #print("The key word is empty or in the skip list")
        return None
    
    keyword = quote(key_word.encode('utf8'))
    print('duration = {0}'.format(search_period[period]))
   
    # Sample request in Google search 
    # https://www.google.com/search?q=%E5%8F%B0%E7%A9%8D%E9%9B%BB&client=safari&rls=en&biw=1780&bih=946&source=lnt&tbs=cdr%3A1%2Ccd_min%3A7%2F1%2F2019%2Ccd_max%3A9%2F30%2F2019&tbm=nws
    res = requests.get("https://www.google.com/search?q=" + keyword + "&client=safari&rls=en&biw=1780&bih=946&source=lnt&tbs=cdr%3A1%2Ccd_" + search_period[period], verify=False)
    
    if res.status_code != 200:
        return articles

    headline = []
    soup = BeautifulSoup(res.text, 'lxml')
    a = soup.find_all('a') 
    for i in a:
        k = i.get('href')
        #print(k)
        try:
            m = re.search("(?P<url>https?://[^\s]+)", k)
            n = m.group(0)
            rul = n.split('&')[0]
            domain = urlparse(rul)
            if(re.search('google.com', domain.netloc)) or (re.search('zh.wikipedia.org', domain.netloc)):
                continue
            else:
                headline.append(rul)
        except:
            continue

    #print('total number of the news: {0}'.format(len(headline)))

    # Only iterate 100 posts
    for h in headline[0:100]:
        try:

            resp = requests.get(h,  allow_redirects=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            test = soup.findAll(text = re.compile(key_word))
            
            if len(test) == 0:
                print('Keyword {0} not found in webpage {1}'.format(key_word, h))
                continue
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
        except KeyboardInterrupt:
            print("Someone closed the program")
        
        """
        try:
            res1 = requests.get(h)
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
        except KeyboardInterrupt:
            print("Someone closed the program")
        """

        # Concatenate all news together
        soup1 = BeautifulSoup(resp.content, "html.parser")
        lines = soup1.findAll('p')
        cont = ''
        for l in lines:
            cont += l.text
        articles[h] = cont
        #print(cont)


    return articles


def parse_csv(file_name = "None", dest_path = "./", period=""):
    with open(file_name, encoding='utf8') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            print(row)
            if len(row) == 0:
                break
            if len(row) >= 1:
                msg0 = search(row[0], period)
                if msg0 != None:
                    save_data(msg0, row[0], dest_path, period)
                
                if sys.argv[1] != "Relationship.csv" and sys.argv[1] != "test.txt" and "company.txt" not in sys.argv[1] :
                    msg1 = search(row[1], period)
                    if msg1 != None:
                        save_data(msg1, row[1], dest_path, period)
           
                    msg2 = search(row[2], period)
                    if msg2 != None:
                        save_data(msg2, row[2], dest_path, period)

    return True


def save_data(articles, file_name, path, period=""):
    file_name = file_name.replace(" ", "_")
    file_name = file_name.replace("/", "")
    print('file name = {0}'.format(file_name))
    dataset = path + "news_" + file_name + "_" + period + ".json"

    # save to json....
    with open(dataset, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)


if __name__== "__main__":
    print("This is news crawler")
    print('file = {0}, path = {1}'.format(sys.argv[1], sys.argv[2]))
    
    #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    """
    for QQQ in search_period:
        print('period = {0}'.format(QQQ))
        data = parse_csv(sys.argv[1], sys.argv[2], QQQ)
    """
    QQQ = "Q5"
    print('period = {0}'.format(QQQ))
    data = parse_csv(sys.argv[1], sys.argv[2], QQQ)
    
    
