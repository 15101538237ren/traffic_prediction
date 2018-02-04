# -*- coding: utf-8 -*-

from traffic_prediction import base
from traffic_prediction import settings
import os, json, urllib2, math, simplejson, datetime, pickle
import numpy as np

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
    region_point_counts = [0 for item in range(base.N_LNG * base.N_LAT)]

    for geo_point in geo_points_list:
        _ , lngtitude, latitude = geo_point
        region_id = -1 # 默认区域编号是-1，如果点的经纬度不在最大区域内时取-1

        # 如果当前点的经纬度在最大的经纬度范围内
        if (base.MIN_LNG <= lngtitude and lngtitude <= base.MAX_LNG and base.MIN_LAT <= latitude and latitude <= base.MAX_LAT):

            i_LNG = int(math.ceil((float(lngtitude) - base.MIN_LNG) / base.LNG_DELTA)) - 1
            j_LAT = int(math.ceil((float(latitude) - base.MIN_LAT) / base.LAT_DELTA)) - 1

            region_id = i_LNG * base.N_LAT + j_LAT
            region_point_counts[region_id] += 1  ##region id内的事件数量
        region_ids.append(region_id)
    return region_ids, region_point_counts

##获取起始结束时间段内时间、经纬度
def get_geo_points_from(dt_start, dt_end, time_segment, type = "violation", write = True):
    if type == "violation":
        if time_segment > -1:
            points_in_time_segment = settings.violation_time_segment_list[time_segment] #获取给定time_segment内所有点
        else:
            points_in_time_segment = settings.violation_geo_points_list
    elif type == "accident":
        if time_segment > -1:
            points_in_time_segment = settings.accident_time_segment_list[time_segment]
        else:
            points_in_time_segment = settings.accident_geo_points_list

    start_index, end_index = base.get_geo_time_idxs(points_in_time_segment, dt_start, dt_end)
    points_in_time_segment_and_date_segment = points_in_time_segment[start_index : end_index + 1]

    if write:
        file_to_wrt_path = settings.os.path.join(settings.BASE_DIR, "static", "points.json")
        file_to_wrt = open(file_to_wrt_path,"w")

        geo_points_to_dump = []
        for geo_point in points_in_time_segment_and_date_segment:
            geo_point_tmp = {}
            geo_point_tmp["lng"] = geo_point[1]
            geo_point_tmp["lat"] = geo_point[2]
            geo_point_tmp["create_time"] = geo_point[0]
            geo_points_to_dump.append(geo_point_tmp)

        js_str = simplejson.dumps(geo_points_to_dump, use_decimal=True,cls=base.DatetimeJSONEncoder)
        file_to_wrt.write(js_str)
    return points_in_time_segment_and_date_segment

def generate_grid_timelines_for_beijing(from_dt, end_dt, out_data_file):
    violation_points = get_geo_points_from(from_dt, end_dt, -1, type="violation", write=True)
    if len(violation_points):
        _, region_point_counts = label_region(violation_points)

        output_file = open(out_data_file,"w")

        for it in range(base.N_LNG * base.N_LAT):
            out_str = "delete rect_" + str(it) + ";\n"
            output_file.write(out_str)

        for i_LNG in range(base.N_LNG):
            for j_LAT in range(base.N_LAT):
                id = i_LNG * base.N_LAT + j_LAT
                min_lng1 = base.LNG_COORDINATES[i_LNG]
                max_lng1 = base.LNG_COORDINATES[i_LNG + 1]
                min_lat1 = base.LAT_COORDINATES[j_LAT]
                max_lat1 = base.LAT_COORDINATES[j_LAT + 1]
                # center_lng = (min_lng1 + max_lng1)/2.0
                # center_lat = (min_lat1 + max_lat1)/2.0
                point_cnt_of_id = region_point_counts[id]

                if point_cnt_of_id == 0:
                    color = 'white'
                elif point_cnt_of_id == 1:
                    color = 'orange'
                else:
                    color = 'red'
                out_str ='''var rect_'''+str(id)+''' = new BMap.Polygon([
                                new BMap.Point(''' + str(min_lng1) + ''',''' + str(min_lat1) + '''),
                                new BMap.Point(''' + str(max_lng1) + ''',''' + str(min_lat1) + '''),
                                new BMap.Point(''' + str(max_lng1) + ''',''' + str(max_lat1) + '''),
                                new BMap.Point(''' + str(min_lng1) + ''',''' + str(max_lat1) + ''')
                            ], {strokeColor:"red", strokeWeight:1, strokeOpacity:1,fillColor:"'''+color+'''",fillOpacity:0.5});\n
                            map.addOverlay(rect_'''+str(id)+''');\n'''
                            # var point_'''+str(id)+''' = new BMap.Point(''' + str(center_lng) + ''',''' + str(center_lat) + ''');\n
                            # var marker_'''+str(id)+''' = new BMap.Marker(point_'''+str(id)+''');\n
                            # var label_'''+str(id)+''' = new BMap.Label("'''+str(accident_cnt_of_id)+'''", {position: point_'''+str(id)+''',offset: new BMap.Size(20, -10)});\n
                            # label_'''+str(id)+'''.setStyle({color: "black",fontSize: "12px",border: "0",backgroundColor: "0.0"});\n
                            # marker_'''+str(id)+'''.setLabel(label_'''+str(id)+''');\n
                            # map.addOverlay(marker_'''+str(id)+''');'''
                output_file.write(out_str)
        output_file.close()
        return 0
    else:
        return -1

##生成时间段内时间频率矩阵list
def generate_region_point_frequency(start_time, end_time, day_interval, time_segment):
    region_point_frequency_matrix_in_time_segment = []
    left_datetimes, right_datetimes = base.generate_timelist(start_time, end_time, day_interval)
    for lidx, from_dt in enumerate(left_datetimes):
        end_dt = right_datetimes[lidx]

        day = (end_dt - from_dt).total_seconds() / 60.0 / 60.0 / 24.0

        points_in_time_segment_and_date_segment = get_geo_points_from(from_dt, end_dt, time_segment, type=settings.POINT_TYPE)
        _, region_point_counts_in_time_segment_and_date_segment = label_region(points_in_time_segment_and_date_segment)
        region_point_frequency = [i/day for i in region_point_counts_in_time_segment_and_date_segment]  # 事件发生频率
        region_point_frequency_matrix_in_time_segment.append(region_point_frequency) # list内每一个元素为一个矩阵

    return region_point_frequency_matrix_in_time_segment

def generate_frequency_matrix_by_time_segment(start_time, end_time, day_interval, outpkl_path):

    frequency_matrix_dict_by_time_segment = {}

    for i in range(6):
        # 创建字典，key为time_segment值，value为矩阵list，list内元素为segment对应的频率矩阵
        frequency_matrix_dict_by_time_segment[i] = generate_region_point_frequency(start_time, end_time, day_interval, i)

    with open(outpkl_path, 'wb') as pickle_file:
        pickle.dump(frequency_matrix_dict_by_time_segment, pickle_file, -1)
        print "dump %s sucessful" % outpkl_path

    return frequency_matrix_dict_by_time_segment


outpkl_path = os.path.join(base.data_dir, "intermediate", "region_point_frequency_matrix_by_time_segment.pkl")
frequency_matrix_by_time_segment = generate_frequency_matrix_by_time_segment(settings.START_TIME, settings.END_TIME, settings.DAYS_INTERVAL, outpkl_path)

if __name__ == "__main__":
    pass