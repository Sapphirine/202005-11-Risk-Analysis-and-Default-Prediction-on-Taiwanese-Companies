# This file is used to retrieve posts from twitter.
#
# Usage:
# python tweet_crawler.py ${CSV_FILE} ${DEST_FOLDER}
#
# Example:
# python tweet_crawler.py computer_peripherals.csv ./global_industry/
#
#


import os
import csv
import sys
import json
import tweepy as tw
import pandas as pd
import pickle
import datetime

ACCESS_TOKEN = '1288560438-SHG2abKSS9EFU3U6Uz2SdIDNaJcECoJhbUlfDgT'     # your access token
ACCESS_TOKEN_SECRET = 'Ol3RvqVkNk5qA1hNftpZ7WuMMnaEyhVjxWVkfXOskKegi'    # your access token secret
CONSUMER_KEY = 'KIPwjwW1UeY6TRHQ4a85yHL18'     # your API key
CONSUMER_SECRET = 'YUZFZhOwqp30XQ2MVzuQoZmvw50HK90IlRuEMaP0saxNGZDmfZ'  # your API secret key

skip_list = ['電腦及周邊設備', '上游', '下游', '筆記型電腦', '精簡型電腦', '伺服器', '安全監控系統', '其他電腦及週邊設備']

search_start = {
        "Q1": datetime.datetime(2019, 1, 1, 0, 0, 0),
        "Q2": datetime.datetime(2019, 4, 1, 0, 0, 0),
        "Q3": datetime.datetime(2019, 7, 1, 0, 0, 0),
        "Q4": datetime.datetime(2018, 10, 1, 0, 0, 0)
}

search_end = {
        "Q1": datetime.datetime(2019, 3, 31, 0, 0, 0),
        "Q2": datetime.datetime(2019, 6, 30, 0, 0, 0),
        "Q3": datetime.datetime(2019, 9, 30, 0, 0, 0),
        "Q4": datetime.datetime(2018, 12, 31, 0, 0, 0)
}

def init():
    auth = tw.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tw.API(auth, wait_on_rate_limit=True)

    return api

def post(api=None):
    api.update_status("Look, I'm tweeting from #Python in my #earthanalytics class! @EarthLabCU")


def search(search_words="null", chosen_lang="en", startDate=datetime.datetime(2018, 10, 1, 0, 0, 0), endDate=datetime.datetime(2018, 12, 31, 0, 0, 0)):
    # Define the search term and the date_since date as variables
    print('search word: {0}'.format(search_words))
    print('search period: {0} - {1}'.format(startDate, endDate))

    message = []
    if search_words == "null" or search_words == "" or search_words in skip_list:
        return None 

    # Collect tweets
    tweets = tw.Cursor(api.search,
              q=search_words,
              timeout=30,
              lang=chosen_lang,
              since=startDate).items()
    
    for tweet in tweets:
        print('created date: {0}'.format(tweet.created_at))
        if tweet.created_at < endDate:
            #print(tweet.text)
            print('date={0}, content={1}'.format(tweet.created_at, tweet.text))
            message.append(tweet.text)
    #print(message)

    return message


def parse_csv(file_name = "None", dest_path = "./", period="Q1"):
    with open(file_name) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            #print(row)
            if len(row) == 0:
                break
            if len(row) > 1:
                data = {}
                msg0 = search(row[0], "zh-tw", search_start[period], search_end[period])
                if msg0 != None:
                    data[row[0]] = msg0
                    save_data(data, row[0], dest_path, "zh-tw")
                
                #print('file_name is: {0}'.format(sys.argv[1])) 
                if sys.argv[1] != "Relationship.csv":
                    data = {}
                    msg1 = search(row[1], "en", search_start[period], search_end[period])
                    if msg1 != None:
                        data[row[1]] = msg1
                        save_data(data, row[1], dest_path, "en")
           
                    data = {}
                    msg2 = search(row[2], "en", search_start[period], search_end[period])
                    if msg2 != None:
                        data[row[2]] = msg2
                        save_data(data, row[1], dest_path, "en")

    return True


def save_data(data, file_name, path, lang="eng"):
    file_name = file_name.replace(" ", "_")
    file_name = file_name.replace("/", "")
    print('file name = {0}'.format(file_name))
    dataset = path + "tweet_" + file_name + lang + ".json"

    #with open(dataset, 'wb') as filehandle:
    #    pickle.dump(data, filehandle)
    
    # save to json....
    with open(dataset, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



if __name__== "__main__":
    api = init()
    #post(api)
    #search()
    
    for key in search_start:
        print('Search period: {0}'.format(key))
        data = parse_csv(sys.argv[1], sys.argv[2], key)



