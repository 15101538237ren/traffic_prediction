# -*- coding: utf-8 -*-

from traffic_prediction import base
from traffic_prediction import settings
import os, json, urllib2, math, simplejson

#标记是否是节假日
def label_holiday(geo_points_list):
    holiday_labels = []
    for geo_point in geo_points_list:
        time_of_point, _, _ = geo_point
        date_1 = str(time_of_point)[0:10]
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
    for geo_point in geo_points_list:
        time_of_point, _, _ = geo_point
        vio_hour = time_of_point.hour
        if  vio_hour>= 0 and vio_hour < 7:
            time_segment = base.DAWN
        elif vio_hour >=7 and vio_hour < 9:
            time_segment = base.MORNING_RUSH
        elif vio_hour >=9 and vio_hour < 12:
            time_segment = base.MORNING_WORKING
        elif vio_hour >=12 and vio_hour < 14:
            time_segment = base.NOON
        elif vio_hour >=14 and vio_hour < 20:
            time_segment = base.AFTERNOON
        else:
            time_segment = base.NIGHT
        time_segment_labels.append(time_segment)

    return time_segment_labels

#标记区域id
def label_region(geo_points_list):
    region_ids = []
    for geo_point in geo_points_list:
        _ , lngtitude, latitude = geo_point

        region_id = -1 # 默认区域编号是-1，如果点的经纬度不在最大区域内时取-1

        # 如果当前点的经纬度在最大的经纬度范围内
        if (
                base.MIN_LNG <= lngtitude and lngtitude <= base.MAX_LNG and base.MIN_LAT <= latitude and latitude <= base.MAX_LAT):
            i_LNG = int(math.ceil((float(lngtitude) - base.MIN_LNG) / base.LNG_DELTA)) - 1
            j_LAT = int(math.ceil((float(latitude) - base.MIN_LAT) / base.LAT_DELTA)) - 1

            region_id = i_LNG * base.N_LAT + j_LAT

        region_ids.append(region_id)
    return region_ids

def get_geo_points_from(dt_start, dt_end, type = "violation"):
    call_incidences = Call_Incidence.objects.filter(create_time__range=[dt_start,dt_end])
    file_to_wrt_path = settings.BASE_DIR + os.sep + "static" + os.sep + "points.json"
    file_to_wrt = open(file_to_wrt_path,"w")

    call_incidences_to_dump = []
    for call_incidence in call_incidences:
        call_incidence_tmp = {}
        call_incidence_tmp["lng"] = call_incidence.longitude
        call_incidence_tmp["lat"] = call_incidence.latitude
        call_incidence_tmp["place"] = call_incidence.place
        call_incidence_tmp["create_time"] = call_incidence.create_time
        call_incidences_to_dump.append(call_incidence_tmp)

    js_str = simplejson.dumps(call_incidences_to_dump, use_decimal=True,cls=base.DatetimeJSONEncoder)
    file_to_wrt.write(js_str)

if __name__ == "__main__":
    pass
    # label_holiday(geo_points_list)
    # label_time_segment(geo_points_list)
    # label_region(geo_points_list)