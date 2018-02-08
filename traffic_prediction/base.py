# -*- coding: utf-8 -*-
import os, datetime, math, simplejson, decimal, bisect,time, random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(BASE_DIR, "data")
origin_dir = os.path.join(data_dir, "origin")

SECOND_FORMAT = "%Y-%m-%d %H:%M:%S"

SERVER_URL = "http://www.easybots.cn/api/holiday.php?d="

DAWN = 0; MORNING_RUSH = 1; MORNING_WORKING = 2; NOON = 3; AFTERNOON = 4; NIGHT = 5

segment_list=["DAWN", "MORNING_RUSH", "MORNING_WORKING", "MOON", "AFTERNOON", "NIGHT"]

MIN_LAT = 39.764427; MAX_LAT = 40.033227
MIN_LNG = 116.214834; MAX_LNG = 116.562834
LAT_DELTA = 0.0084; LNG_DELTA = 0.012
SEP = 1000

N_LAT = int(math.ceil((MAX_LAT - MIN_LAT) / LAT_DELTA))
N_LNG = int(math.ceil((MAX_LNG - MIN_LNG) / LNG_DELTA))

LNG_COORDINATES = [MIN_LNG + i_LNG * LNG_DELTA for i_LNG in range(N_LNG + 1)]
LAT_COORDINATES = [MIN_LAT + i_LAT * LAT_DELTA for i_LAT in range(N_LAT + 1)]

GRID_LNG_LAT_COORDS = [[LNG_COORDINATES[i_LNG], LNG_COORDINATES[i_LNG + 1], LAT_COORDINATES[j_LAT], LAT_COORDINATES[j_LAT + 1]]  for i_LNG in range(N_LNG) for j_LAT in range(N_LAT)]

# 输入数据路径, 读取max_lines行, 返回所有点的列表，以及对应时间段的点列表
def read_origin_data_into_geo_point_list(input_file_path, sep="\t",line_end = "\n", max_lines = -1):
    geo_points_list = []
    time_segment_list = [[] for i in range(6)]#6个元素, 每个是个列表, 对应为该时间段的所有点

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

            vio_hour = time_of_point.hour

            if vio_hour >= 0 and vio_hour < 7:
                time_segment = DAWN

            elif vio_hour >= 7 and vio_hour < 9:
                time_segment = MORNING_RUSH

            elif vio_hour >= 9 and vio_hour < 12:
                time_segment = MORNING_WORKING

            elif vio_hour >= 12 and vio_hour < 14:
                time_segment = NOON

            elif vio_hour >= 14 and vio_hour < 20:
                time_segment = AFTERNOON

            else:
                time_segment = NIGHT
            time_segment_list[time_segment].append(geo_point) ##将点添加到相应的segment list中

            line = input_file.readline()
    return geo_points_list, time_segment_list

# 输入时间地理点列表, 输出在(dt_start, dt_end)的时间范围内的点的索引(left_index, right_index)
def get_geo_time_idxs(geo_points_List, dt_start, dt_end):
    time_stamps = [time.mktime(item[0].timetuple()) for item in geo_points_List]

    dt_start_time_stamp = time.mktime(dt_start.timetuple())
    dt_end_time_stamp = time.mktime(dt_end.timetuple())

    left_index = bisect.bisect(time_stamps, dt_start_time_stamp)
    right_index = bisect.bisect(time_stamps, dt_end_time_stamp) - 1

    return [left_index, right_index]

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



error_mapping = {
    "LOGIN_NEEDED": (1, "login needed"),
    "PERMISSION_DENIED": (2, "permission denied"),
    "DATABASE_ERROR": (3, "operate database error"),
    "ONLY_FOR_AJAX": (4, "the url is only for ajax request")
}
class ApiError(Exception):
    def __init__(self, key, **kwargs):
        Exception.__init__(self)
        self.key = key if key in error_mapping else "UNKNOWN"
        self.kwargs = kwargs

def ajax_required(func):
    def __decorator(request, *args, **kwargs):
        if request.is_ajax:
            return func(request, *args, **kwargs)
        else:
            raise ApiError("ONLY_FOR_AJAX")
    return __decorator

def safe_new_datetime(d):
    kw = [d.year, d.month, d.day]
    if isinstance(d, datetime.datetime):
        kw.extend([d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
    return datetime.datetime(*kw)

def safe_new_date(d):
    return datetime.date(d.year, d.month, d.day)

class DatetimeJSONEncoder(simplejson.JSONEncoder):
    """可以序列化时间的JSON"""

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            d = safe_new_datetime(o)
            return d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            d = safe_new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DatetimeJSONEncoder, self).default(o)