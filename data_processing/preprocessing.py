# -*- coding: utf-8 -*-

from traffic_prediction import settings
import base, os, json, urllib2, math

#标记是否是节假日
def label_holiday(geo_points_list):
    holiday_labels = []
    for i in geo_points_list:
        vio_time = geo_points_list[i][0]
        date_1 = str(vio_time)[0:10]
        date = date_1.replace('-', '')
        vop_url_request = urllib2.Request(base.SERVER_URL + date)
        vop_response = urllib2.urlopen(vop_url_request)
        vop_data = json.loads(vop_response.read())
        is_holiday = vop_data[date]
        holiday_labels.append(is_holiday)
    return holiday_labels

#标记时间段
def label_time_segment(geo_points_list):
    time_segment_labels = []

    return time_segment_labels

#标记区域id
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

        region_ids.append(region_id)
    return region_ids
if __name__ == "__main__":
    accident_fp =  os.path.join(base.origin_dir, "accident_loc.tsv")
    geo_points_list = base.read_origin_data_into_geo_point_list(accident_fp, max_lines=10)
    # label_holiday(geo_points_list)
    label_region(geo_points_list)