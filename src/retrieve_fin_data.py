#
# This file is used to retrieve financial data from balance sheets.
# Usage:
# python ./retrieve_fin_data.py ../fin_statements/balance_sheet_{Duration}.csv ../fin_statements/income_statement_{Duration}.csv <DEST_DIR>
#
# Example:
# python ./retrieve_fin_data.py ../fin_statements/balance_sheet_2019_Q4.csv ../fin_statements/income_statement_2019_Q4.csv ../fin_data/
#

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


def parse_csv(file1 = "None", file2 = "None", companies = []):
    fin_data = {}
    
    csvfile1 = open(file1)
    csvfile2 = open(file2)
    balance_sheet_csv = csv.reader(csvfile1, delimiter=',')
    income_statement_csv = csv.reader(csvfile2, delimiter=',')
    
    index = 0
    for row1, row2 in itertools.zip_longest(balance_sheet_csv, income_statement_csv):
        ratios = {}
        #print('row1: {0}, row2: {1}'.format(row1, row2))
        if index == 0:
            index = index +1
            continue

        if row1 == None:
            break

        if row1[4] not in companies:
            #print('not on list: {0}'.format(row1[4]))
            continue

        # logz1: log asset accounting value
        logz1 = math.log(float(row1[7]))     
        ratios['logz1'] = logz1
        
        # logz4: log book to market value
        logz4 = math.log(float(row1[20])*1.0/float(row1[11]))
        ratios['logz4'] = logz4

        # z5
        #print('Name: {0}, row1[9]: {1}, row1[11]: {2}'.format(row1[4], row1[9], row1[11]))
        if row1[9] == "--":
            row1[9] = 0
        z5 = float(row1[9])*1.0/float(row1[11])
        ratios['z5'] = z5
        
        # z7
        z7 = float(row1[10])*1.0/float(row1[20])
        ratios['z7'] = z7

        # z22: quick ratio
        z22 = float(row1[5])*1.0/float(row1[8])
        ratios['z22'] = z22
        
        #print('[1]{0} ratios = {1}'.format(row1[4], ratios))

        if row2[5] != "--" and float(row2[5]) != 0:
            # z11: operating profit margin  
            z11 = float(row2[9])*1.0/float(row2[5])
            ratios['z11'] = z11
            
            # z13
            z13 = float(row2[17])*1.0/float(row2[5])
            ratios['z13'] = z13
            
            # z15: gross profit margin
            z15 = (float(row2[5]) - float(row2[6]))*1.0/float(row2[5])
            ratios['z15'] = z15
        else:
            ratios['z11'] = "NULL"
            ratios['z13'] = "NULL"

        # z17: EPS
        z17 = float(row2[32])
        ratios['z17'] = z17
        
        #print('[2] ratios = {0}'.format(ratios))
        
        # Save all ratios to together
        fin_data[row1[4]] = ratios


    #print('final result: {0}'.format(fin_data))
    return fin_data


def save_data(data, postfix = "2019_Q", dest = "./"):
    dataset = dest + "/ratios" + postfix + ".json"

    # save to json....
    with open(dataset, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__== "__main__":
    # Get company list
    companies = []
    f = open("./company.txt", "r")
    for line in f:
        companies.append(line[:-1])

    #print(companies)

    print("Retrieving numbers from financial statements")
    print('balance sheet = {0}, income statement = {1}'.format(sys.argv[1], sys.argv[2]))
    data = parse_csv(sys.argv[1], sys.argv[2], companies)
    
    tmp = sys.argv[1].replace(".", "_")
    postfix = tmp.split("_")[-3]
    postfix += tmp.split("_")[-2]
    #print('postfix = {0}'.format(postfix))
    
    save_data(data, postfix, sys.argv[3])







