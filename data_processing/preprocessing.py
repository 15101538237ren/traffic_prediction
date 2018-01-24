# -*- coding: utf-8 -*-

from traffic_prediction import settings
import base, os
import json
import urllib2

def label_holiday(geo_points_list):
    holiday_labels = []
    for i in geo_points_list:
        vio_time = geo_points_list[i][0]
        date_1 = str(vio_time)[0:10]
        date = date_1.replace('-', '')
        vop_url_request = urllib2.Request(base.server_url + date)
        vop_response = urllib2.urlopen(vop_url_request)
        vop_data = json.loads(vop_response.read())
        is_holiday = vop_data[date]
        holiday_labels.append(is_holiday)
    return holiday_labels

def label_time_segment(geo_points_list):
    time_segment_labels = []

    return time_segment_labels

if __name__ == "__main__":
    accident_fp =  os.path.join(base.origin_dir, "accident_loc.tsv")
    geo_points_list = base.read_origin_data_into_geo_point_list(accident_fp)
    label_holiday(geo_points_list)