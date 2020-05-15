#
# This file is used to retrieve financial data from balance sheets.
# Usage:
# python ./get_stock_price.py {PATH_TO_BALANCE_SHEET}  {DEST_DIR}
#
# Example:
# python ./get_stock_price.py ../../fin_statements/balance_sheet_2020_Q1.csv  ../data/raw/fin_data/

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.parse import urlparse
import itertools  
import json
import os
import csv
import sys
import math


def parse_csv(file1 = "None", companies = []):
    fin_data = {}
    
    csvfile1 = open(file1)
    balance_sheet_csv = csv.reader(csvfile1, delimiter=',')
    
    index = 0
    for row1 in balance_sheet_csv:
        #print('row1: {0}'.format(row1))
        if index == 0:
            index = index +1
            continue

        if row1 == None:
            break

        if row1[4] not in companies:
            #print('not on list: {0}'.format(row1[4]))
            continue

        # Save all ratios to together
        fin_data[row1[4]] = row1[-1]


    #print('final result: {0}'.format(fin_data))
    return fin_data


def save_data(data, postfix = "2019_Q", dest = "./"):
    dataset = dest + "/stocks" + postfix + ".json"

    # save to json....
    with open(dataset, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__== "__main__":
    # Get company list
    companies = []
    f = open("./company.txt", "r")
    for line in f:
        companies.append(line[:-1])

    print(companies)

    print("Retrieving numbers from financial statements")
    print('balance sheet = {0}, DEST_DIR = {1}'.format(sys.argv[1], sys.argv[2]))
    data = parse_csv(sys.argv[1], companies)
    
    tmp = sys.argv[1].replace(".", "_")
    postfix = tmp.split("_")[-3]
    postfix += tmp.split("_")[-2]
    #print('postfix = {0}'.format(postfix))
    
    save_data(data, postfix, sys.argv[2])







