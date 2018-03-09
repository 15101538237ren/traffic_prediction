# -*- coding: utf-8 -*-

from traffic_prediction import base
from traffic_prediction import settings
import os, json, urllib2, math, simplejson, datetime, time, pickle
import numpy as np
frequency_matrix_dict, max_frequency_dict, left_datetimes_arr, geo_points_list, time_segment_list = None, None, None, None, None
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
        hour = time_of_point.hour
        time_segment = base.time_segment_judge(hour, base.IS_TIME_SEGMENT)
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
def get_geo_points_from(points_in_time_segment, dt_start, dt_end, write = True):

    start_index, end_index = base.get_geo_time_idxs(points_in_time_segment, dt_start, dt_end)
    points_in_time_segment_and_date_segment = points_in_time_segment[start_index : end_index + 1]

    if write:
        file_to_wrt_path = settings.os.path.join(settings.JSON_DIR, "geo_points.json")
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
    geo_points_list_tmp, _ = obtain_origin_data()
    geo_points = get_geo_points_from(geo_points_list_tmp, from_dt, end_dt, write=True)
    if len(geo_points):
        _, region_point_counts = label_region(geo_points)

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
def generate_region_point_frequency(time_segment_list_tmp,left_datetimes, right_datetimes, time_segment_i):
    max_frequency = -999999

    region_point_frequency_matrix_in_time_segment = []
    for lidx, from_dt in enumerate(left_datetimes):
        end_dt = right_datetimes[lidx]
        day = (end_dt - from_dt).total_seconds() / 60.0 / 60.0 / 24.0
        points_in_time_segment_and_date_segment = get_geo_points_from(time_segment_list_tmp, from_dt, end_dt, write=False)
        _, region_point_counts_in_time_segment_and_date_segment = label_region(points_in_time_segment_and_date_segment)

        region_point_frequency = []  # 事件发生频率
        for region_point_count in region_point_counts_in_time_segment_and_date_segment:
            freq = region_point_count/day/base.TIME_SEGMENT_HOURS[time_segment_i]
            region_point_frequency.append(freq)

            max_frequency = freq if freq > max_frequency else max_frequency
        region_point_frequency_matrix_in_time_segment.append(region_point_frequency) # list内每一个元素为一个矩阵

    return region_point_frequency_matrix_in_time_segment, max_frequency

def output_freq_time_series_data(day_intervals_str, time_segment_i, left_datetimes, freq_matrix):
    out_dir_fp = os.path.join(base.freqency_data_dir, day_intervals_str, base.SEGMENT_FILE_PRE + str(time_segment_i))
    if not os.path.exists(out_dir_fp):
        os.makedirs(out_dir_fp)

    header = 'datetime\tavg_count\n'
    for rid in range(base.N_LNG * base.N_LAT):
        out_file_fp = os.path.join(out_dir_fp, str(rid) + '.tsv')
        with open(out_file_fp, "w") as out_file:
            out_file.write(header)

            for lidx, ldt in enumerate(left_datetimes):
                ldt_str = (ldt + base.get_timedelta_of_timesegment(time_segment_i)).strftime(base.SECOND_FORMAT)
                freq_str = str(round(freq_matrix[lidx][rid],4))
                ltw = ldt_str + '\t' + freq_str + '\n'
                out_file.write(ltw)
    print 'write freq of %s %s sucessful' % (day_intervals_str, str(time_segment_i))

def obtain_origin_data():
    global geo_points_list, time_segment_list
    if not geo_points_list:
        geo_points_list, time_segment_list = base.read_origin_data_into_geo_point_list(base.FILE_FP, max_lines=base.MAX_LINES)

    return [geo_points_list, time_segment_list]

def generate_frequency_matrix(start_time, end_time, day_intervals, outpkl_path, dump=False):
    frequency_matrix_dict = {}
    max_frequency_dict = {}
    left_datetimes_arr = []
    _, time_segment_list_tmp = obtain_origin_data()
    for idx, day_interval in enumerate(day_intervals):
        print 'start generate freq matrix of %s' % settings.DAYS_INTERVALS_LABEL[idx]
        t0 = time.time()

        left_datetimes, right_datetimes = base.generate_timelist(start_time, end_time, day_interval)
        frequency_matrix_dict[day_interval] = {}
        max_frequency_dict[day_interval] = {}
        max_frequency_of_day = -9999999

        for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
            print 'start time_segment %d' % time_segment_i
            tt0 = time.time()
            # 创建字典，key为time_segment值，value为矩阵list，list内元素为segment对应的频率矩阵
            frequency_matrix_dict[day_interval][time_segment_i], max_freq = generate_region_point_frequency(time_segment_list_tmp[time_segment_i],left_datetimes, right_datetimes, time_segment_i)
            max_frequency_of_day = max_freq if max_freq > max_frequency_of_day else max_frequency_of_day

            tt1 = time.time()
            print 'finish time_segment %d in %.2f seconds' % (time_segment_i, tt1 - tt0)
        max_frequency_dict[day_interval] = max_frequency_of_day
        t1 = time.time()
        print 'finish generate freq matrix of %s in %.2f seconds' % (settings.DAYS_INTERVALS_LABEL[idx], t1-t0)
        left_datetimes_arr.append(left_datetimes)
    if dump:
        with open(outpkl_path, 'wb') as pickle_file:
            pickle.dump(frequency_matrix_dict, pickle_file, -1)
            pickle.dump(max_frequency_dict, pickle_file, -1)
            pickle.dump(left_datetimes_arr, pickle_file, -1)
            print "dump %s sucessful" % outpkl_path
    return [frequency_matrix_dict, max_frequency_dict, left_datetimes_arr]

def generate_color_matrix(freq_matrix, max_val):
    color_matrix = []
    for freq_sub_matrix in freq_matrix:
        color_matrix.append([int(round(255 * min(freq / (0.5 * max_val), 1.0), 2)) for freq in freq_sub_matrix])
    return color_matrix

def obtain_frequency_matrix():
    global frequency_matrix_dict, max_frequency_dict, left_datetimes_arr

    if not frequency_matrix_dict:
        if not os.path.exists(base.freq_matrix_pkl_path):
            frequency_matrix_dict, max_frequency_dict, left_datetimes_arr = generate_frequency_matrix(settings.START_TIME, settings.END_TIME, settings.DAYS_INTERVALS , base.freq_matrix_pkl_path, dump=True)
        else:
            print "start load pickle file %s" % (base.freq_matrix_pkl_path)

            with open(base.freq_matrix_pkl_path, "rb") as pickle_file:
                frequency_matrix_dict = pickle.load(pickle_file)
                max_frequency_dict = pickle.load(pickle_file)
                left_datetimes_arr = pickle.load(pickle_file)
    return frequency_matrix_dict, max_frequency_dict, left_datetimes_arr

def generate_freq_data_pipline():
    frequency_matrix_dict, max_frequency_dict, left_datetimes_arr = obtain_frequency_matrix()
    for didx, day_interval in enumerate(settings.DAYS_INTERVALS):
        day_interval_str = settings.DAYS_INTERVALS_LABEL[didx]
        left_datetimes = left_datetimes_arr[didx]

        print 'start generate freq data of %s' % day_interval_str
        t0 = time.time()
        for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
            print 'start time_segment %d' % time_segment_i
            tt0 = time.time()
            freq_matrix = frequency_matrix_dict[day_interval][time_segment_i]
            output_freq_time_series_data(day_interval_str, time_segment_i, left_datetimes, freq_matrix)
            tt1 = time.time()
            print 'finish time_segment %d in %.2f seconds' % (time_segment_i, tt1 - tt0)
        t1 = time.time()
        print 'finish generate freq data of %s in %.2f seconds' % (day_interval_str, t1 - t0)

def generate_train_and_test_data(freq_data_dir, training_out_fp, testing_out_fp, sequence_length, training_datetime_slot, testing_datetime_slot):
    training_data_seq, testing_data_seq = [], []

    seq_len = sequence_length + 1
    for rid in range(base.N_LNG * base.N_LAT):
        region_train_data_origin, region_testing_data_origin = [], []
        
        freq_data_fp = os.path.join(freq_data_dir, str(rid) + '.tsv')
        freq_data = open(freq_data_fp, 'rb').read()
        
        for idx, line_item in enumerate(freq_data.split('\n')):
            if idx and line_item != "":
                line_item_arr = line_item.split("\t")
                dti = datetime.datetime.strptime(line_item_arr[0], base.SECOND_FORMAT)
                freq = float(line_item_arr[1])
                
                if training_datetime_slot[0] <= dti <= training_datetime_slot[1]:
                    region_train_data_origin.append(freq)
                elif testing_datetime_slot[0] <= dti <= testing_datetime_slot[1]:
                    region_testing_data_origin.append([rid, dti, freq])
    
        for index in range(len(region_train_data_origin) - seq_len + 1):
            training_data_seq.append(region_train_data_origin[index: index + seq_len])  #得到长度为seq_len+1的向量，最后一个作为label
        
        for index in range(len(region_testing_data_origin) - seq_len + 1):
            arr_to_append = [region_testing_data_origin[index + seq_len - 1][0],
                             region_testing_data_origin[index + seq_len - 1][1].strftime(base.SECOND_FORMAT)]
            for idx in range(index, index + seq_len):
                arr_to_append.append(region_testing_data_origin[idx][2])
            testing_data_seq.append(arr_to_append)
    
    base.write_sequence_array_into_file(training_out_fp, training_data_seq)
    base.write_sequence_array_into_file(testing_out_fp, testing_data_seq)

def generate_train_and_test_data_pipline():
    for didx, day_interval in enumerate(settings.DAYS_INTERVALS):
        day_interval_str = settings.DAYS_INTERVALS_LABEL[didx]
        for time_segment_i in range(base.TIME_SEGMENT_LENGTH):
            freqency_data_dir = os.path.join(base.freqency_data_dir, day_interval_str, base.SEGMENT_FILE_PRE + str(time_segment_i))
            training_dir_fp = os.path.join(base.training_data_dir, day_interval_str)
            testing_dir_fp = os.path.join(base.testing_data_dir, day_interval_str)

            dirs_to_create = [training_dir_fp, testing_dir_fp]
            for dtc in dirs_to_create:
                if not os.path.exists(dtc):
                    os.makedirs(dtc)

            training_data_fp = os.path.join(training_dir_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + '.tsv')
            testing_data_fp = os.path.join(testing_dir_fp, base.SEGMENT_FILE_PRE + str(time_segment_i) + '.tsv')
            generate_train_and_test_data(freqency_data_dir, training_data_fp, testing_data_fp, base.SEQUENCE_LENGTH_DICT[settings.TIME_PERIODS[day_interval_str]],
                                         settings.TRAINING_DATETIME_SLOT, settings.TESTING_DATETIME_SLOT)

def load_prediction_result(int_time_period, time_segment_i):
    datetime_dict = {}
    datetime_list, datetime_str_list = [], []
    frequency_matrix_dict_real, frequency_matrix_dict_predicted = {}, {}
    frequency_matrix_real, frequency_matrix_predicted = [], []
    real_frequency, predicted_frequency = {rid :[] for rid in range(base.N_LNG * base.N_LAT)}, {rid :[] for rid in range(base.N_LNG * base.N_LAT)}

    max_frequency = -999999
    day_interval_str = settings.TIME_PERIODS_INT_TO_STR[int_time_period]
    predict_result_fp = os.path.join(base.predict_result_dir, day_interval_str, base.SEGMENT_FILE_PRE + str(time_segment_i) + ".tsv")

    with open(predict_result_fp, "r") as predict_result_f:
        lines = predict_result_f.read().split("\n")
        for line in lines:
            line_arr = line.split("\t")
            datetime_str = line_arr[1]
            if datetime_str not in datetime_dict.keys():
                datetime_dict[datetime_str] = 1
                frequency_matrix_dict_real[datetime_str] = [0. for rid in range(base.N_LNG * base.N_LAT)]
                frequency_matrix_dict_predicted[datetime_str] = [0. for rid in range(base.N_LNG * base.N_LAT)]
            region_id = int(line_arr[0])
            real_freq = float(line_arr[2])
            predicted_freq = float(line_arr[3])
            frequency_matrix_dict_real[datetime_str][region_id] = real_freq
            frequency_matrix_dict_predicted[datetime_str][region_id] = predicted_freq
            real_frequency[region_id].append(real_freq)
            predicted_frequency[region_id].append(predicted_freq)
    for datetime_key in sorted(datetime_dict.keys()):
        datetime_list.append(datetime.datetime.strptime(datetime_key, base.SECOND_FORMAT))
        datetime_str_list.append(datetime_key.split(" ")[0])
        frequency_matrix_real.append(frequency_matrix_dict_real[datetime_key])
        frequency_matrix_predicted.append(frequency_matrix_dict_predicted[datetime_key])
        relative_max = max(np.array(frequency_matrix_dict_real[datetime_key]).max(), np.array(frequency_matrix_dict_predicted[datetime_key]).max())
        max_frequency = max_frequency if relative_max < max_frequency else relative_max

    del datetime_dict, frequency_matrix_dict_real, frequency_matrix_dict_predicted
    return datetime_list, frequency_matrix_real, frequency_matrix_predicted, max_frequency, datetime_str_list, real_frequency, predicted_frequency
if __name__ == "__main__":
    generate_freq_data_pipline()
    generate_train_and_test_data_pipline()