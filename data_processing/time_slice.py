# -*- coding:utf-8 -*-
##划分时间段 将24小时划分为12个段，作为新的attribute
import urllib2, json
import csv
import datetime,time

server_url = "http://www.easybots.cn/api/holiday.php?d="
with open('D://traffic_prediction//data//addRegionID.csv','r') as f1:
    with open('D://traffic_prediction//data//addRegionIDandTimeSlice.csv','w')as f2:
        reader = csv.reader(f1)
        writer = csv.writer(f2)
        for row in csv.reader(f1):
            row[1]=row[1].replace('/','-')
            vio_time = datetime.datetime.strptime(row[1],'%Y-%m-%d %H:%M')
            vio_hour = vio_time.hour

            date_1=str(vio_time)[0:10]
            date = date_1.replace('-','')
            vop_url_request = urllib2.Request(server_url + date)
            vop_response = urllib2.urlopen(vop_url_request)
            vop_data = json.loads(vop_response.read())
            is_holiday= vop_data[date]  ##判断是否为节假日 0:weekday 1：weekend 2：
            print date +' '+ vop_data[date]
            writer.writerow(row + [vio_hour/2]+ [is_holiday])

f1.close()
f2.close()