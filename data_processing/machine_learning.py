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
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping,TensorBoard
from traffic_prediction import base, settings
warnings.filterwarnings("ignore")

BATCH_SIZE = 512
EPOCHS = 1
VALIDATION_RATIO = 0.05

def load_data(training_dir_fp, testing_dir_fp, sep = '\t', line_end = '\n'):
    print('loading data from %s and %s' %(training_dir_fp, testing_dir_fp))

    train, x_train, y_train, x_test, y_test, time_segs, region_ids, date_times = [], [], [], [], [], [], [], []
    for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
        training_data_fp = os.path.join(training_dir_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + '.tsv')
        with open(training_data_fp, 'r') as train_f:
            for idx, item in enumerate(train_f.read().split(line_end)):
                if idx and item != "":
                    train.append([float(it) for it in item.split(sep)])
        testing_data_fp = os.path.join(testing_dir_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + '.tsv')
        with open(testing_data_fp, 'r') as testing_f:
            for idx, item in enumerate(testing_f.read().split(line_end)):
                if idx and item != "":
                    item_arr = item.split(sep)
                    time_segs.append(time_segment_i)
                    region_ids.append(item_arr[0])
                    date_times.append(item_arr[1])
                    x_test.append([float(it) for it in item_arr[2: -1]])
                    y_test.append(float(item_arr[-1]))

    print("train_test_ratio %.2f" % (float(len(y_train))/ len(y_test)))

    train = np.array(train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)
    time_segs = np.array(time_segs)
    region_ids= np.array(region_ids)
    date_times = np.array(date_times)

    #划分train、test
    np.random.shuffle(train)
    x_train = train[:, :-1]
    y_train = train[:, -1]

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    print ('x_train shape', x_train.shape)
    print('y_train shape:', y_train.shape)
    print('x_test shape', x_test.shape)
    print('y_test shape:', y_test.shape)

    return [x_train, y_train, x_test, y_test, time_segs, region_ids, date_times]

def build_lstm_model(layers, dropout_rate = 0.2, activation = 'relu', loss = "mse", optimizer = "rmsprop"):  #layers [1,50,100,1]
    print('> Data Loaded. Compiling...')
    model = Sequential()

    model.add(LSTM(input_dim=layers[0],output_dim=layers[1],return_sequences=True))
    model.add(Dropout(dropout_rate))

    model.add(LSTM(layers[2],return_sequences=False))
    model.add(Dropout(dropout_rate))

    model.add(Dense(output_dim=layers[3]))
    model.add(Activation(activation))

    start = time.time()
    model.compile(loss=loss, optimizer=optimizer)
    print("Compilation Time : ", time.time() - start)
    return model

#直接全部预测
def predict_point_by_point(model, data):
    predicted = model.predict(data)
    print('predicted shape:', np.array(predicted).shape)
    predicted = np.reshape(predicted, (predicted.size,))
    return predicted

def model_training_and_saving_pipline():
    for didx, day_interval in enumerate(settings.DAYS_INTERVALS):

        day_interval_str = settings.DAYS_INTERVALS_LABEL[didx]
        training_dir_fp = os.path.join(base.training_data_dir, day_interval_str)
        testing_dir_fp = os.path.join(base.testing_data_dir, day_interval_str)
        model_dir_fp = os.path.join(base.model_dir, day_interval_str)
        prediction_fp = os.path.join(base.predict_result_dir, day_interval_str)
        dirs_to_create = [model_dir_fp, prediction_fp]
        for dtc in dirs_to_create:
            if not os.path.exists(dtc):
                os.makedirs(dtc)
        [x_train, y_train, x_test, y_test, time_segs, region_ids, date_times] = load_data(training_dir_fp, testing_dir_fp)

        seq_len = base.SEQUENCE_LENGTH_DICT[settings.TIME_PERIODS[day_interval_str]]
        model = build_lstm_model([1, seq_len, 2 * seq_len, 1])

        model_path = os.path.join(model_dir_fp, "lstm_model.h5")
        model_saver = ModelCheckpoint(filepath=model_path, verbose=1)
        model.fit(x_train, y_train, batch_size=BATCH_SIZE, nb_epoch=EPOCHS, validation_split= VALIDATION_RATIO, callbacks=[model_saver])

        predicted_y = predict_point_by_point(model, x_test)

        for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
            tidx_list = [tidx for tidx, titem in enumerate(time_segs) if titem == time_segment_i]
            predict_result_fp = os.path.join(prediction_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + ".tsv")
            with open(predict_result_fp, "w") as predict_f:
                ltws = []
                for tidx in tidx_list:
                    ltw = '\t'.join([region_ids[tidx], date_times[tidx], str(y_test[tidx]), str(predicted_y[tidx])])
                    ltws.append(ltw)
                predict_f.write('\n'.join(ltws))
if __name__ == "__main__":
    model_training_and_saving_pipline()