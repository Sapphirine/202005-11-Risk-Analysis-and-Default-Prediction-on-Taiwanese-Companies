#
# This file is used to train the LSTM model
#  
# Before running it, copy "company.txt", 
# "sentiment.json" and "label.json" to the current folder. 
#
# Usage:
# python ./rnn_lstm.py {PATH_TO_FIN_DATA} 
#
# Example:
# python ./rnn_lstm.py ../data/raw/fin_data
#


import collections
import matplotlib.pyplot as plt
import numpy as np
import keras.backend as K
import keras
import json
import sys
import os

from keras.preprocessing.sequence import pad_sequences
from keras.utils.generic_utils import CustomObjectScope
from keras.utils.generic_utils import get_custom_objects
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Embedding
from keras.layers import LSTM
#from keras.layers import Dense, Activation, Flatten

COMPANIES="./company.txt"
SENTI_PATH="./sentiment.json"
duration = ["Q1", "Q2"]

class activation_wrapper(object):
    def __init__(self, func):
        self.func = func
        self.__name__ = 'ReLU'

    def __call__(self, *args, **kwargs):
        def _xdfunc(x):
            return self.func(x, *args, **kwargs)
        return _xdfunc

wrapped_relu = activation_wrapper(keras.activations.relu)

def relu_advanced(x):
    return K.relu(x, max_value=4.0, threshold=3.0)

# Combine the FIN ratios and sentiment data together
# Read the whole year in one time
def load_train_data(fin_dir, title="ratios2019", period=None):
    files_path = [os.path.join(fin_dir, x) for x in os.listdir(fin_dir)]
    #print(files_path)

    #title = "ratios2019"
    if period == None:
        period = duration
    
    # Load JSON files
    year_data = []
    for QQ in period:
        q_data = []
        fff = title + QQ + ".json"
        for filename in files_path:
            if fff in filename:
                #print(fff)
                with open(filename) as f:
                    q_data = json.load(f)
                    year_data.append(q_data)
        
    with open(SENTI_PATH) as f:
        senti_data = json.load(f)
    
    with open(COMPANIES) as f:
        companies = [line.strip() for line in f]
    #print(companies) 
    
    final_data = []
    all_keys = []
    for ccc in companies:
        timestep = []
        for i in range(0, len(period)):
            #print('the period is {0}'.format(period[i]))
            if ccc in year_data[i]:
                find_str = ccc + "_" + period[i]
                combined = np.array(list(year_data[i][ccc].values()))
                if find_str in senti_data:
                    combined = np.concatenate((combined, np.array(senti_data[find_str])))
            timestep.append(combined)
        
        #print('[{0}] company data = {1}'.format(period[i], timestep))
        #np.info(np.array(timestep))
        final_data.append(np.array(timestep))
    
    padded = pad_sequences(final_data, padding='post')
    
    #np.info(padded)
    #print(padded)
    return np.asarray(padded)


def load_labels(label_path, period=None):
    with open(COMPANIES) as f:
        companies = [line.strip() for line in f]

    with open(label_path) as f:
        labels = json.load(f)
    
    if period == None:
        period = duration
    
    final_data = []
    # TODO: Normalize the output ??
    for ccc in companies:
        timestep = []
        for i in range(0, len(period)):
            #print('the period is {0}'.format(period[i]))
            find_str = ccc + "_" + period[i]
            if labels[find_str] == None or labels[find_str] == "NA":
                # If there is no label, use "3.0" temporarily.
                # print('No label found. {0}'.format(ccc))
                timestep.append(3.0/1.0)
            else:
                timestep.append(labels[find_str]/1.0)
        #print('[{0}] company data = {1}'.format(period[i], timestep))
        final_data.append(np.array(timestep))
       

    return np.array(final_data)


def train_data(x_train, y_train):
    #x_train = sequence.pad_sequences(x_train)
    max_features = len(x_train) * len(x_train[0])

    model = Sequential()
    
    print('X (row, col) = {0}'.format(x_train.shape))
    print('Y (row, col) = {0}'.format(y_train.shape))
    
    # Add a LSTM layer with 128 internal units.
    model.add(LSTM(128, return_sequences=True, activation='relu'))
    model.add(Dropout(0.1))
    
    model.add(Flatten())
    model.add(Dense(2, activation=relu_advanced))
    #model.add(Dense(2, activation='linear'))
    model.compile(loss='mse',
                  optimizer='rmsprop',
                  metrics=['accuracy'])

    model.fit(x_train, y_train, epochs=10)

    # save LSTM modele
    model.save('lstm_model.h5')


    return model

def test_data(x_test, y_test, model):
    print('X (row, col) = {0}'.format(x_test.shape))
    print('Y (row, col) = {0}'.format(y_test.shape))
    
    score = model.evaluate(x_test, y_test, batch_size=len(y_test))
    
    print(model.metrics_names)
    print('the final score is: {0}'.format(score))


    return score
    

def predict_data(X):
    get_custom_objects().update({'relu_advanced': relu_advanced})
    #print(ret)

    # load model from single file
    model = load_model('lstm_model.h5',  custom_objects={"activate": relu_advanced})
   
    model.summary()
    yhat = model.predict(X)
    #yhat = model.predict_proba(X)
    print(yhat)

    return yhat


if __name__== "__main__":
    X_train = load_train_data(sys.argv[1])
    #np.info(X_train)

    Y_train = load_labels("./label.json")
    #np.info(Y_train)

    model = train_data(X_train, Y_train)

    X_test = load_train_data(sys.argv[1], period=list(["Q3", "Q4"]))
    Y_test = load_labels("./label.json", list(["Q3", "Q4"]))
    test_data(X_test, Y_test, model)


