# -*- coding: utf-8 -*-
from traffic_prediction import settings
import base, os, math

def label_holiday(geo_points_list):
    holiday_labels = []
    #pass
    return holiday_labels

def label_time_segment(geo_points_list):
    time_segment_labels = []
    return time_segment_labels

def label_region(geo_points_list):
    region_ids = []
    for geo_point in geo_points_list:
        _ , lngtitude, latitude = geo_point

        region_id = -1 # 默认区域编号是-1，如果点的经纬度不在最大区域内时取-1

        # 如果当前点的经纬度在最大的经纬度范围内
        if (base.MIN_LNG <= lngtitude and lngtitude <= base.MAX_LNG and base.MIN_LAT <= latitude and latitude <= base.MAX_LAT):
            i_LNG = int(math.ceil((float(lngtitude) - base.MIN_LNG) / base.LNG_DELTA)) - 1
            j_LAT = int(math.ceil((float(latitude) - base.MIN_LAT) / base.LAT_DELTA)) - 1

            region_id = i_LNG * base.N_LAT + j_LAT

        region_id.append(region_id)
    return region_ids
if __name__ == "__main__":
    accident_fp =  os.path.join(base.origin_dir, "accident_loc.tsv")
    geo_points_list = base.read_origin_data_into_geo_point_list(accident_fp)
    label_holiday(geo_points_list)
    label_region(geo_points_list)