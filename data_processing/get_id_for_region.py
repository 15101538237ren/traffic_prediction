# -*- coding:utf-8 -*-
import math
import numpy as np
import csv

## 五环
min_lat = 39.764427
max_lat = 40.033227#40.028983
min_lng = 116.214834
max_lng = 116.562834#116.554975
x_pi = math.pi * 3000.0 / 180.0
d_lat = 0.0042
d_lng = 0.006
min_lng_transfered = -0.174
min_lat_transfered = -0.1344

n_lat_delta_origin = (max_lat - min_lat) / d_lat
n_lat_delta = int(math.ceil(n_lat_delta_origin)) + 1  ##向上取整
n_lng_delta_origin = (max_lng - min_lng) / d_lng
n_lng_delta = int(math.ceil(n_lng_delta_origin)) + 1
lng_coors = [min_lng + i * d_lng for i in range(n_lng_delta)]  # 从0到n-1
lat_coors = [min_lat + i * d_lat for i in range(n_lat_delta)]
n_lng = len(lng_coors) - 1
n_lat = len(lat_coors) - 1

def get_id_for_region(lng,lat):
    lng_transfered = lng - 116.388834
    lat_transfered = lat - 39.898827
    i = (lng_transfered - min_lng_transfered)/d_lng
    num_lng = math.ceil(i)
    j = (lat_transfered - min_lat_transfered)/d_lat
    num_lat = math.ceil(j)
    return int((num_lng - 1)* n_lng + num_lat)

with open('D://traffic_prediction//data//test.csv','r') as f1:
    with open('D://traffic_prediction//data//output.csv','w')as f2:
        reader = csv.reader(f1)
        writer = csv.writer(f2)
        for row in csv.reader(f1):
            lng = float(row[2])
            lat = float(row[3])
            id = get_id_for_region(lng,lat)
            print ("lng:%f lat:%f id:%d" %(lng,lat,id))
            writer.writerow(row + [id])
f1.close()
f2.close()