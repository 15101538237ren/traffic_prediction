# -*- coding: utf-8 -*-

from __future__ import print_function

import time, os
import warnings
import numpy as np
import matplotlib.pyplot as plt
from numpy import newaxis
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from traffic_prediction import base

warnings.filterwarnings("ignore")

def load_data(filename, seq_len, train_sample_ratio):
    f = open(filename, 'rb').read()
    data = []
    for idx, item in enumerate(f.split('\n')):
        if idx and item != "":
            data.append(float(item.split("\t")[1]))

    print('data len:',len(data))
    print('sequence len:',seq_len)

    sequence_length = seq_len + 1
    result = []
    for index in range(len(data) - sequence_length):
        result.append(data[index: index + sequence_length])  #得到长度为seq_len+1的向量，最后一个作为label

    print('result len:',len(result))
    print('result shape:',np.array(result).shape)
    print(result[:1])

    result = np.array(result)

    #划分train、test
    row = int(round(train_sample_ratio * result.shape[0]))
    train = result[:row, :]
    np.random.shuffle(train)
    x_train = train[:, :-1]
    y_train = train[:, -1]
    x_test = result[row:, :-1]
    y_test = result[row:, -1]

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    return [x_train, y_train, x_test, y_test]

def build_model(layers):  #layers [1,50,100,1]
    model = Sequential()

    model.add(LSTM(input_dim=layers[0],output_dim=layers[1],return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(layers[2],return_sequences=False))
    model.add(Dropout(0.2))

    model.add(Dense(output_dim=layers[3]))
    model.add(Activation("linear"))

    start = time.time()
    model.compile(loss="mse", optimizer="rmsprop")
    print("Compilation Time : ", time.time() - start)
    return model

#直接全部预测
def predict_point_by_point(model, data):
    predicted = model.predict(data)
    print('predicted shape:',np.array(predicted).shape)  #(412L,1L)
    predicted = np.reshape(predicted, (predicted.size,))
    return predicted

def plot_results(predicted_data, true_data, filename):
    fig = plt.figure(facecolor='white')
    ax = fig.add_subplot(111)
    ax.plot(true_data, label='True Data')
    plt.plot(predicted_data, label='Prediction')
    plt.legend()
    plt.show()
    # plt.savefig(filename+'.png')

if __name__=='__main__':
    # day_interval = '3_days'
    # time_segment_i = 1
    # region_id = 398
    # input_dir_fp = os.path.join(base.freqency_data_dir, day_interval, 'seg_' + str(time_segment_i))
    # time_series_fp = os.path.join(input_dir_fp, str(region_id) + '.tsv')

    day_interval = '3_days'
    time_segment_i = 2
    input_dir_fp = os.path.join(base.freqency_data_dir, day_interval, 'seg_' + str(time_segment_i))
    time_series_fp = os.path.join(input_dir_fp, 'full_sequences.tsv')


    global_start_time = time.time()
    epochs  = 1
    seq_len = 50
    train_sample_ratio = 0.9
    print('> Loading data... ')

    X_train, y_train, X_test, y_test = load_data(time_series_fp, seq_len, train_sample_ratio)

    print('X_train shape:',X_train.shape)  #(3709L, 50L, 1L)
    print('y_train shape:',y_train.shape)  #(3709L,)
    print('X_test shape:',X_test.shape)    #(412L, 50L, 1L)
    print('y_test shape:',y_test.shape)    #(412L,)

    print('> Data Loaded. Compiling...')

    model = build_model([1, 50, 100, 1])

    model.fit(X_train,y_train,batch_size=512,nb_epoch=epochs,validation_split=0.05)

    point_by_point_predictions = predict_point_by_point(model, X_test)
    print('point_by_point_predictions shape:',np.array(point_by_point_predictions).shape)  #(412L)

    print('Training duration (s) : ', time.time() - global_start_time)

    plot_results(point_by_point_predictions, y_test, 'point_by_point_predictions')