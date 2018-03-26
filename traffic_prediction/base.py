# -*- coding: utf-8 -*-
import os, datetime, math, simplejson, decimal, bisect,time, random

from numpy import unicode

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POINT_TYPE = "violation"
data_dir = os.path.join(BASE_DIR, "data")
origin_dir = os.path.join(data_dir, "origin")

accident_fp = os.path.join(origin_dir, "accident_loc.tsv")
violation_fp = os.path.join(origin_dir, "violation_loc.tsv")
FILE_FP = accident_fp if POINT_TYPE == "accident" else violation_fp

MAX_LINES = -1

SECOND_FORMAT = "%Y-%m-%d %H:%M:%S"
ONLY_TIME_FORMAT = "%H:%M:%S"
SERVER_URL = "http://www.easybots.cn/api/holiday.php?d="

IS_TIME_SEGMENT = True

TIME_SEGMENT_DIR_NAME = 'time_segment_data' if IS_TIME_SEGMENT else 'hour_data'
TIME_SEGMENT_LENGTH = 6 if IS_TIME_SEGMENT else 24
TIME_SEGMENT_START_TIME = {0: 0, 1: 7, 2: 9, 3: 12, 4: 14, 5: 20}
TIME_SEGMENT_START_TIME_DICT = {item: datetime.datetime(2000, 1, 1, TIME_SEGMENT_START_TIME[item], 0, 0, 0).strftime(ONLY_TIME_FORMAT) for item in range(TIME_SEGMENT_LENGTH)} if IS_TIME_SEGMENT else {item: datetime.datetime(2000, 1, 1, item, 0, 0, 0).strftime(ONLY_TIME_FORMAT) for item in range(TIME_SEGMENT_LENGTH)}
SEGMENT_FILE_PRE = 'seg_'
MODEL_SELECTION = 'arma'
SEQUENCE_LENGTH_DICT = {1: 29, 3: 19, 7: 4, 30: 1}

DAWN = 0; MORNING_RUSH = 1; MORNING_WORKING = 2; NOON = 3; AFTERNOON = 4; NIGHT = 5

TIME_SEGMENT_HOURS = {DAWN: 7., MORNING_RUSH: 2., MORNING_WORKING: 3., NOON: 2., AFTERNOON:6. , NIGHT: 4.} if IS_TIME_SEGMENT else {i: 1. for i in range(TIME_SEGMENT_LENGTH)}

TIME_SEGMENTS_LABELS = {u'凌晨 0:00-7:00': 0, u'早高峰 7:00-9:00': 1, u'早工作 9:00-12:00': 2,
                        u'中午 12:00-14:00': 3, u'下午 14:00-20:00': 4, u'晚间 20:00-24:00': 5} if IS_TIME_SEGMENT \
                        else {unicode(str(item)): item for item in range(TIME_SEGMENT_LENGTH)}

FREQUENCY_DEGREE_DICT = {0:[1,0,0,0,0,0], 1:[0,1,0,0,0,0], 2:[0,0,1,0,0,0], 3:[0,0,0,1,0,0], 4:[0,0,0,0,1,0], 5:[0,0,0,0,0,1]}

# freqency_data_dir = os.path.join(data_dir, "intermediate", "freqency_data_new", POINT_TYPE, TIME_SEGMENT_DIR_NAME)
freqency_data_dir = os.path.join(data_dir, "intermediate", "freqency_data", POINT_TYPE, TIME_SEGMENT_DIR_NAME)
training_data_dir = os.path.join(data_dir, "intermediate", "training_data", POINT_TYPE, TIME_SEGMENT_DIR_NAME)
testing_data_dir = os.path.join(data_dir, "intermediate", "testing_data", POINT_TYPE, TIME_SEGMENT_DIR_NAME)
model_dir = os.path.join(data_dir, "intermediate", "model", POINT_TYPE, TIME_SEGMENT_DIR_NAME)
predict_result_dir = os.path.join(data_dir, "intermediate", "predict_result", POINT_TYPE, TIME_SEGMENT_DIR_NAME)

dirs_to_create = [freqency_data_dir, training_data_dir, training_data_dir, model_dir, predict_result_dir]

for dtc in dirs_to_create:
    if not os.path.exists(dtc):
        os.makedirs(dtc)

freq_matrix_pkl_path = os.path.join(freqency_data_dir, "region_point_freq_matrix.pkl")

MIN_LAT = 39.764427; MAX_LAT = 40.033227
MIN_LNG = 116.214834; MAX_LNG = 116.562834
LAT_DELTA = 0.0084; LNG_DELTA = 0.012
SEP = 1000

N_LAT = int(math.ceil((MAX_LAT - MIN_LAT) / LAT_DELTA))
N_LNG = int(math.ceil((MAX_LNG - MIN_LNG) / LNG_DELTA))

LNG_COORDINATES = [MIN_LNG + i_LNG * LNG_DELTA for i_LNG in range(N_LNG + 1)]
LAT_COORDINATES = [MIN_LAT + i_LAT * LAT_DELTA for i_LAT in range(N_LAT + 1)]

GRID_LNG_LAT_COORDS = [[LNG_COORDINATES[i_LNG], LNG_COORDINATES[i_LNG + 1], LAT_COORDINATES[j_LAT], LAT_COORDINATES[j_LAT + 1]]  for i_LNG in range(N_LNG) for j_LAT in range(N_LAT)]


# 读取tab分隔的文件(input_file_path) 的第target_col_index, 返回该列的所有值到一个list
def read_tab_seperated_file_and_get_target_column(target_col_index, input_file_path, start_line= 1, sep="\t",line_end = "\n"):
    ret_value_list = []
    line_counter = 0
    with open(input_file_path, "r") as input_file:
        line = input_file.readline()
        while line:
            line_counter += 1
            if line_counter >= start_line:
                line_contents = line.split(sep)
                led = line_contents[target_col_index].strip(line_end)
                ret_value_list.append(led)
            line = input_file.readline()
    return ret_value_list
#事件频率等级
def frequency_degree_judge(freq):
    if freq>=0.0 and freq < 0.2:
        frequency_degree = 0
    elif freq>=0.2 and freq < 0.4:
        frequency_degree = 1
    elif freq>= 0.4 and freq < 0.6:
        frequency_degree = 2
    elif freq>= 0.6 and freq < 0.8:
        frequency_degree = 3
    elif freq>= 0.8 and freq < 1.0:
        frequency_degree = 4
    else:
        frequency_degree = 5
    return frequency_degree

def time_segment_judge(hour, is_time_segment = True):
    if is_time_segment:
        if hour >= 0 and hour < 7:
            time_segment = DAWN

        elif hour >= 7 and hour < 9:
            time_segment = MORNING_RUSH

        elif hour >= 9 and hour < 12:
            time_segment = MORNING_WORKING

        elif hour >= 12 and hour < 14:
            time_segment = NOON

        elif hour >= 14 and hour < 20:
            time_segment = AFTERNOON
        else:
            time_segment = NIGHT
        return time_segment
    else:
        return hour

def get_timedelta_of_timesegment(time_segment_i):
    if IS_TIME_SEGMENT:
        time_segment_delta_hours = [0, 7, 9, 12, 14, 20]
        return datetime.timedelta(hours= time_segment_delta_hours[time_segment_i])
    else:
        return datetime.timedelta(hours= time_segment_i)

# 输入数据路径, 读取max_lines行, 返回所有点的列表，以及对应时间段的点列表
def read_origin_data_into_geo_point_list(input_file_path, sep="\t",line_end = "\n", max_lines = -1):
    print ('start reading %s' % input_file_path)

    t0 = time.time()
    geo_points_list = []
    time_segment_list = [[] for i in range(TIME_SEGMENT_LENGTH)]#TIME_SEGMENT_LENGTH个元素, 每个是个列表, 对应为该时间段的所有点

    line_counter = 0
    with open(input_file_path, "r") as input_file:
        line = input_file.readline()
        while line:
            line_counter += 1
            if max_lines > 0 and line_counter > max_lines:
                break
            line_contents = line.strip(line_end).split(sep)

            time_of_point = datetime.datetime.strptime(line_contents[1], SECOND_FORMAT)
            longtitude = float(line_contents[2])
            latitude = float(line_contents[3])

            geo_point = [time_of_point, longtitude, latitude]
            geo_points_list.append(geo_point)

            hour = time_of_point.hour
            time_segment = time_segment_judge(hour, IS_TIME_SEGMENT)
            time_segment_list[time_segment].append(geo_point) ##将点添加到相应的segment list中
            line = input_file.readline()
    t1 = time.time()
    print ('finish reading %s in %.2f seconds' % (input_file_path, t1 - t0))
    return geo_points_list, time_segment_list

#给定起始、结束日期时间
def generate_timelist(start_datetime, end_datetime, time_delta):
    left_datetimes = []
    right_datetimes = []

    left_dt = start_datetime
    while left_dt < end_datetime:
        right_dt = end_datetime if left_dt + time_delta > end_datetime else left_dt + time_delta

        left_datetimes.append(left_dt)
        right_datetimes.append(right_dt)

        left_dt = right_dt
    return left_datetimes, right_datetimes

# 输入时间地理点列表, 输出在(dt_start, dt_end)的时间范围内的点的索引(left_index, right_index)
def get_geo_time_idxs(geo_points_List, dt_start, dt_end):
    time_stamps = [time.mktime(item[0].timetuple()) for item in geo_points_List]

    dt_start_time_stamp = time.mktime(dt_start.timetuple())
    dt_end_time_stamp = time.mktime(dt_end.timetuple())

    left_index = bisect.bisect(time_stamps, dt_start_time_stamp)
    right_index = bisect.bisect(time_stamps, dt_end_time_stamp) - 1

    return [left_index, right_index]

def write_sequence_array_into_file(out_fp, seq_arr, sep="\t", line_end = "\n"):
    with open(out_fp, "w") as out_f:
        ltws = []
        for titem in seq_arr:
            ltw = sep.join([str(item) for item in titem])
            ltws.append(ltw)
        out_f.write(line_end.join(ltws))
    print ("writing %s sucessful" % out_fp)