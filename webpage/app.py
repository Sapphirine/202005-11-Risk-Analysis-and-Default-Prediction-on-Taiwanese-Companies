# -*- coding: utf-8 -*-
"""
Created on Sat May  2 16:52:56 2020

@author: Wayne
"""

import json

from flask import Flask, render_template, request
import pandas as pd
from flask import jsonify
import sys
sys.path.append("..")
from src.graphdb import get_egonet

app = Flask(__name__)


@app.route('/')
def hello_world():
    print("hello world")
    payload = {}
    payload['status'] = 'success'
    payload['message'] = 'Hello world!'

    return jsonify(payload)

@app.route('/index', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        comp_name = request.form['name']
        
        with open('prediction.json', 'r', encoding='utf-8') as f:
            scoredata = json.load(f)
        score = scoredata[comp_name][:3]
        
        with open('js_fin.json', 'r', encoding='utf-8') as f:
            findata = json.load(f)
        if comp_name in findata:
            fin = findata[comp_name]
        else:
            fin = []
            
        graph = get_egonet(comp_name)
        
        with open('js_sent.json', 'r', encoding='utf-8') as f:
            sentdata = json.load(f)
        sent = sentdata[comp_name]
        
        with open('js_stock.json', 'r', encoding='utf-8') as f:
            stockdata = json.load(f)
        if comp_name in stockdata:
            stock = stockdata[comp_name]
        else:
            stock = []
            
        return render_template("index2.html", name = comp_name, graph = graph, \
                               sent = sent, stock = stock, fin = fin, score = score)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)