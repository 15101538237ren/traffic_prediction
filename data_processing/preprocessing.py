# -*- coding: utf-8 -*-
from traffic_prediction import settings
import base, os

def label_holiday(geo_points_list):
    holiday_labels = []
    #pass
    return holiday_labels

def label_time_segment(geo_points_list):
    time_segment_labels = []
    return time_segment_labels

if __name__ == "__main__":
    accident_fp =  os.path.join(base.origin_dir, "accident_loc.tsv")
    geo_points_list = base.read_origin_data_into_geo_point_list(accident_fp)
    label_holiday(geo_points_list)