# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
sys.path.append("..")
from sklearn.svm import SVR
import time, os, math, keras
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from statsmodels.tsa.stattools import ARMA
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
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

        testing_rid_and_dti_and_y_data_fp = os.path.join(testing_dir_fp, base.SEGMENT_FILE_PRE + str(
            time_segment_i) + '_rid_and_dti_and_y_data.tsv')
        testing_x_data_seq_fp = os.path.join(testing_dir_fp,
                                             base.SEGMENT_FILE_PRE + str(time_segment_i) + '_x_data.tsv')
        with open(testing_x_data_seq_fp, 'r') as testing_x_data_f:
            for idx, item in enumerate(testing_x_data_f.read().split(line_end)):
                if idx and item != "":
                    item_arr = item.split(sep)
                    x_test.append([float(it) for it in item_arr])

        with open(testing_rid_and_dti_and_y_data_fp, 'r') as testing_rid_and_dti_and_y_data_f:
            for idx, item in enumerate(testing_rid_and_dti_and_y_data_f.read().split(line_end)):
                if idx and item != "":
                    item_arr = item.split(sep)
                    time_segs.append(time_segment_i)
                    region_ids.append(item_arr[0])
                    date_times.append(item_arr[1])
                    y_test.append(float(item_arr[2]))

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

#base line model 直接从freq的data生成training和testing的序列
def baseline_model_training_and_saving(model_name, classifier):
    for didx, day_interval in enumerate(settings.DAYS_INTERVALS):
        day_interval_str = settings.DAYS_INTERVALS_LABEL[didx]
        for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
            for seq_len in base.SEQUENCE_LENGTHS:
                print(model_name + ' ' + day_interval_str + ' time_segment: ' + str(time_segment_i) + 'seq len: ' + str(seq_len))
                seq_dir_name = base.SEQ_LEN_FILE_PRE + str(seq_len)
                prediction_fp = os.path.join(base.predict_result_dir, model_name, day_interval_str, seq_dir_name)
                dirs_to_create = [prediction_fp]
                for dtc in dirs_to_create:
                    if not os.path.exists(dtc):
                        os.makedirs(dtc)
                predict_result_fp = os.path.join(prediction_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + ".tsv")
                training_dir_fp = os.path.join(base.training_data_dir, day_interval_str, seq_dir_name)
                testing_dir_fp = os.path.join(base.testing_data_dir, day_interval_str, seq_dir_name)
                [x_train, y_train, x_test, y_test, _, region_ids, date_times] = load_data(training_dir_fp,
                                                                                                  testing_dir_fp)

                classifier.fit(x_train, y_train)
                predicted_y = classifier.predict(x_test)
                with open(predict_result_fp, "w") as predict_f:
                    ltws = []
                    for tidx, dt_i in enumerate(date_times):
                        ltw = '\t'.join([region_ids[tidx], date_times[tidx], str(y_test[tidx]),
                                str(predicted_y[tidx])])
                        ltws.append(ltw)
                    predict_f.write('\n'.join(ltws))

def generate_error_file(model_name):
    for didx, day_interval in enumerate(settings.DAYS_INTERVALS):
        day_interval_str = settings.DAYS_INTERVALS_LABEL[didx]
        for seq_len in base.SEQUENCE_LENGTHS:
            seq_dir_name = base.SEQ_LEN_FILE_PRE + str(seq_len)
            prediction_fp = os.path.join(base.predict_result_dir, model_name, day_interval_str, seq_dir_name)
            error_fp = os.path.join(prediction_fp, base.ERROR_FILE_NAME)
            with open(error_fp, "w") as e_f:
                for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
                    predict_result_fp = os.path.join(prediction_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + ".tsv")
                    error = []
                    squaredError = []
                    absError = []
                    error_str_pre = day_interval_str + '_seg_' + str(time_segment_i)
                    with open(predict_result_fp, "r") as prdp:
                        lines = prdp.read().split("\n")
                        for line in lines:
                            if line != "":
                                line_arr = line.split("\t")
                                real_data = float(line_arr[2])
                                predict_data = float(line_arr[3])
                                val = real_data - predict_data
                                error.append(val)
                                squaredError.append(val * val)
                                absError.append(abs(val))
                    erw = '\t'.join([error_str_pre,
                                         str(round(sum(squaredError) / len(squaredError), 4)),  # mse
                                         str(round(math.sqrt(sum(squaredError) / len(squaredError)), 4)),  # rmse
                                         str(round(sum(absError) / len(absError), 4))]) + '\n'  # mae
                    e_f.write(erw)

def baseline_model_pipline():
    lr = LinearRegression()
    lasso = Lasso(alpha = 0.1)
    ridge = Ridge(alpha=.5)
    svr = SVR(kernel='linear')
    dtr = DecisionTreeRegressor()
    rfr = RandomForestRegressor(n_estimators=20)
    abr = AdaBoostRegressor(n_estimators=50)
    gbr = GradientBoostingRegressor(n_estimators=100)
    mlp = MLPRegressor(solver='adam', activation = 'relu', alpha=1e-5, hidden_layer_sizes=(100, 100), random_state=1)
    classifiers = [lr, lasso, ridge,  svr, dtr, rfr, abr, gbr, mlp] #,
    classifier_names = ['lr', 'lasso', 'ridge', 'svr', 'dtr', 'rfr', 'abr', 'gbr', 'mlp'] #,

    for midx, item in enumerate(classifiers):
        print('model ' + classifier_names[midx])
        baseline_model_training_and_saving(classifier_names[midx], item)
        generate_error_file(classifier_names[midx])

def lstm_model_training_and_saving_pipline():
    for didx, day_interval in enumerate(settings.DAYS_INTERVALS):
        day_interval_str = settings.DAYS_INTERVALS_LABEL[didx]
        for seq_length in base.SEQUENCE_LENGTHS:
            print('model lstm ' + day_interval_str + ' seq len ' + str(seq_length))
            seq_dir_name = base.SEQ_LEN_FILE_PRE + str(seq_length)
            training_dir_fp = os.path.join(base.training_data_dir, day_interval_str, seq_dir_name)
            testing_dir_fp = os.path.join(base.testing_data_dir, day_interval_str, seq_dir_name)
            model_dir_fp = os.path.join(base.model_dir, day_interval_str, seq_dir_name)
            prediction_fp = os.path.join(base.predict_result_dir, 'lstm', day_interval_str, seq_dir_name)
            dirs_to_create = [model_dir_fp, prediction_fp]
            for dtc in dirs_to_create:
                if not os.path.exists(dtc):
                    os.makedirs(dtc)
            [x_train, y_train, x_test, y_test, time_segs, region_ids, date_times] = load_data(training_dir_fp, testing_dir_fp)

            x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
            model = build_lstm_model([1, seq_length, 2 * seq_length, 1])

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


def lstm_model_param_trying_pipline():
    number_of_epoch = 3
    seq_length = 99

    tail_name = '_epoch_' + str(number_of_epoch)
    for didx, day_interval in enumerate(settings.DAYS_INTERVALS):
        day_interval_str = settings.DAYS_INTERVALS_LABEL[didx]
        print('model lstm ' + day_interval_str + ' seq len ' + str(seq_length))
        seq_dir_name = base.SEQ_LEN_FILE_PRE + str(seq_length)
        training_dir_fp = os.path.join(base.training_data_dir, day_interval_str, seq_dir_name)
        testing_dir_fp = os.path.join(base.testing_data_dir, day_interval_str, seq_dir_name)

        model_dir_fp = os.path.join(base.model_dir, day_interval_str, seq_dir_name + tail_name)
        prediction_fp = os.path.join(base.predict_result_dir, 'lstm', day_interval_str)
        dirs_to_create = [model_dir_fp, prediction_fp]
        for dtc in dirs_to_create:
            if not os.path.exists(dtc):
                os.makedirs(dtc)
        [x_train, y_train, x_test, y_test, time_segs, region_ids, date_times] = load_data(training_dir_fp,
                                                                                          testing_dir_fp)

        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

        predictor = Predictor(prediction_fp, seq_dir_name, x_test, y_test, time_segs, region_ids, date_times)

        model = build_lstm_model([1, seq_length, 2 * seq_length, 1])

        model_path = os.path.join(model_dir_fp, "lstm_model.h5")
        model_saver = ModelCheckpoint(filepath=model_path, verbose=1)
        model.fit(x_train, y_train, batch_size=BATCH_SIZE, nb_epoch= number_of_epoch, validation_split=VALIDATION_RATIO,
                  callbacks=[model_saver, predictor])


class Predictor(keras.callbacks.Callback):
    def __init__(self, prediction_fp, seq_dir_name, x_test, y_test, time_segs, region_ids, date_times):
        super(Predictor, self).__init__()
        self.prediction_fp = prediction_fp
        self.seq_dir_name = seq_dir_name
        self.x_test = x_test
        self.y_test = y_test
        self.time_segs = time_segs
        self.region_ids = region_ids
        self.date_times = date_times

    def on_epoch_end(self, epoch, logs={}):
        print("Predictor start at epoch %d" % epoch)

        predict_result_dir_fp = os.path.join(self.prediction_fp, self.seq_dir_name + '_epoch_' + str(epoch))
        if not os.path.exists(predict_result_dir_fp):
            os.makedirs(predict_result_dir_fp)

        predicted_y = predict_point_by_point(self.model, self.x_test)
        for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
            tidx_list = [tidx for tidx, titem in enumerate(self.time_segs) if titem == time_segment_i]
            predict_result_fp = os.path.join(predict_result_dir_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + ".tsv")

            with open(predict_result_fp, "w") as predict_f:
                ltws = []
                for tidx in tidx_list:
                    ltw = '\t'.join(
                        [self.region_ids[tidx], self.date_times[tidx], str(self.y_test[tidx]), str(predicted_y[tidx])])
                    ltws.append(ltw)
                predict_f.write('\n'.join(ltws))

def arma_model_training_and_saving_pipline():
    for didx, day_interval in enumerate(settings.DAYS_INTERVALS):
        day_interval_str = settings.DAYS_INTERVALS_LABEL[didx]
        for seq_length in base.SEQUENCE_LENGTHS:
            print('model arma ' + day_interval_str + ' seq len ' + str(seq_length))
            seq_dir_name = base.SEQ_LEN_FILE_PRE + str(seq_length)
            prediction_fp = os.path.join(base.predict_result_dir, 'arma', day_interval_str, seq_dir_name)
            dirs_to_create = [prediction_fp]
            for dtc in dirs_to_create:
                if not os.path.exists(dtc):
                    os.makedirs(dtc)
            for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
                time_str = " " + base.TIME_SEGMENT_START_TIME_DICT[time_segment_i]
                input_dir = os.path.join(base.freqency_data_dir, day_interval_str, 'seg_' + str(time_segment_i))
                predict_result_fp = os.path.join(prediction_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + ".tsv")
                with open(predict_result_fp, "w") as predict_f:
                    for rid in range(base.N_LNG * base.N_LAT):
                        print("now region " + str(rid))
                        df = pd.read_csv(os.path.join(input_dir, str(rid) + '.tsv'), sep='\t', lineterminator='\n', header=0, index_col='datetime',
                                         encoding='utf-8')
                        df.index = pd.to_datetime(df.index)
                        ts = df['avg_count']  # 生成pd.Series对象
                        ps = qs = [item for item in range(4, -1, -1)]
                        fit_success = False
                        ts_pre = ts[settings.TIME_PERIODS_TEST_DATES[0] + time_str: settings.TIME_PERIODS_TEST_DATES[1] + time_str]
                        ts_post = ts[settings.TIME_PERIODS_TEST_DATES[1] + time_str: settings.TIME_PERIODS_TEST_DATES[2] + time_str]
                        dts = [datetime.utcfromtimestamp((item - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')).strftime(base.SECOND_FORMAT) for item in list(ts_post.index.values)]
                        ts_post = list(ts_post.values)

                        for p in ps:
                            for q in qs:
                                try:
                                    arma_moddel = ARMA(ts_pre, (p, q)).fit()

                                    fit_success = True
                                    predict_series = arma_moddel.predict(settings.TIME_PERIODS_TEST_DATES[1] + time_str, settings.TIME_PERIODS_TEST_DATES[2] + time_str,
                                                                           dynamic=True)
                                    temp_predict_results = list(predict_series.values)
                                    for item in range(len(ts_post)):
                                        pdr = temp_predict_results[item]
                                        if pdr != pdr:
                                            pdr = 0.0

                                        val = ts_post[item] - pdr
                                        ltw = '\t'.join([str(rid), dts[item],
                                                         str(round(ts_post[item], 4)),   #真实值
                                                         str(round(pdr, 4)),      #预测值
                                                         str(p),
                                                         str(q)]) + '\n'
                                        predict_f.write(ltw )
                                except ValueError as e:
                                    pass
                                except np.linalg.linalg.LinAlgError as e:
                                    pass
                                if fit_success:
                                    break
                            if fit_success:
                                break

if __name__ == "__main__":
    SERVER = False
    if SERVER == True:
        lstm_model_training_and_saving_pipline()
        arma_model_training_and_saving_pipline()
    else:
        baseline_model_pipline()


















