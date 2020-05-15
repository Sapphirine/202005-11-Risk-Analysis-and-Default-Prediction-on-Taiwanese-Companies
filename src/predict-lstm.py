#
# This file is used to do the default prediction
# using the LSTM model we trained
#
# Usage:
#
#
# Example:
#
#

from rnn_lstm import *


if __name__== "__main__":
    print("Predict the default risk.")

    X_input = load_train_data(sys.argv[1], title="ratios2019", period=list(["Q1", "Q1"]))
    trainPredict = predict_data(X_input)
    
    #trainPredict = scaler.inverse_transform(trainPredict)

