# -*- coding:utf-8 -*-
import math
import numpy as np
import csv

## 五环

x_pi = math.pi * 3000.0 / 180.0

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