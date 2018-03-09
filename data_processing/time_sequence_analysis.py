# -*- coding: utf-8 -*-

from traffic_prediction import base
from traffic_prediction import settings
from statsmodels.tsa.stattools import adfuller, acf, ARMA
import statsmodels.api as sm
import os, json, urllib2, math, simplejson, datetime, time, pickle
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.graphics.api import qqplot

# 移动平均图
def draw_trend(timeSeries, size):
    f = plt.figure(facecolor='white')
    # 对size个数据进行移动平均
    rol_mean = timeSeries.rolling(window=size).mean()
    # 对size个数据进行加权移动平均
    rol_weighted_mean = pd.ewma(timeSeries, span=size)

    timeSeries.plot(color='blue', label='Original')
    rol_mean.plot(color='red', label='Rolling Mean')
    rol_weighted_mean.plot(color='black', label='Weighted Rolling Mean')
    plt.legend(loc='best')
    plt.title('Rolling Mean')
    plt.show()

def draw_time_series(timeSeries):
    f = plt.figure(facecolor='white')
    timeSeries.plot(color='blue')
    plt.show()

# 均方根检验平稳性, p-value越小, 越平稳
def unit_root_test(ts):
    dftest = adfuller(ts)
    # 对上述函数求得的值进行语义描述
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print dfoutput

# 自相关和偏相关图，默认阶数为31阶
def draw_acf_pacf(ts, lags=31):
    f = plt.figure(facecolor='white')
    ax1 = f.add_subplot(211)
    plot_acf(ts, lags=lags, ax=ax1)
    ax2 = f.add_subplot(212)
    plot_pacf(ts, lags=lags, ax=ax2)
    plt.show()

# 判断是否是高斯白噪声, 看最后一列前十二行的检验概率，小于给定的水平，比如0.05、0.10则不是白噪声序列。
def ljung_box_test(ts):
    r, q, p = acf(ts, qstat=True)
    data = np.c_[range(1, 41), r[1:], q, p]
    table = pd.DataFrame(data, columns=['lag', "AC", "Q", "Prob(>Q)"])
    print(table.set_index('lag'))

# 残差检验与画图
def residual_test(residual,lags =31):
    # plot acf and pacf
    fig = plt.figure(facecolor='white')
    ax1 = fig.add_subplot(211)
    fig = plot_acf(residual.values.squeeze(), lags=lags, ax=ax1)
    ax2 = fig.add_subplot(212)
    fig = plot_pacf(residual, lags=lags, ax=ax2)
    plt.show()

    # Durbin-Watson test: 2, no autocorrelation; 4: negtive autocorrelation; 0: positive autocorrelation
    #print sm.stats.durbin_watson(arma_moddel.resid.values)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    fig = qqplot(residual, line='q', ax=ax, fit=True)
    plt.show()

    ljung_box_test(residual)

# 用ARMA模型预测时间序列, p, q 为模型参数
def time_seq_prediction_by_arma(ts, time_str, p=1 , q=1):
    draw_time_series(ts)
    draw_acf_pacf(ts)
    # unit_root_test(ts)
    arma_moddel = ARMA(ts, (p, q)).fit()
    # print(arma_moddel.aic, arma_moddel.bic, arma_moddel.hqic)
    # residual_test(arma_moddel.resid)
    predict_sunspots = arma_moddel.predict('2017-01-01' + time_str, '2017-02-27' + time_str)  #
    print(predict_sunspots)
    fig, ax = plt.subplots(facecolor='white')
    ax = ts.ix['2016-01-01'+ time_str:].plot(ax=ax)
    predict_sunspots.plot(ax=ax)
    plt.show()

if __name__ == "__main__":
    day_interval = '3_days'
    time_segment_i = 2
    region_id = 326
    input_dir_fp = os.path.join(base.freqency_data_dir, day_interval, 'seg_' + str(time_segment_i))
    time_series_fp = os.path.join(input_dir_fp, str(region_id) + '.tsv')

    df = pd.read_csv(time_series_fp, sep='\t', lineterminator='\n', header= 0, index_col='datetime', encoding='utf-8')
    df.index = pd.to_datetime(df.index)
    ts = df['avg_count']  # 生成pd.Series对象
    time_str = ' 09:00:00'
    time_seq_prediction_by_arma(ts, time_str, p=3, q=1)
