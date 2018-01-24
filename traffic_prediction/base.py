# -*- coding: utf-8 -*-
import os, datetime, math, simplejson, decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(BASE_DIR, "data")
origin_dir = os.path.join(data_dir, "origin")

SECOND_FORMAT = "%Y-%m-%d %H:%M:%S"

SERVER_URL = "http://www.easybots.cn/api/holiday.php?d="

DAWN = 0; MORNING_RUSH = 1; MORNING_WORKING = 2; NOON = 3; AFTERNOON = 4; NIGHT = 5

MIN_LAT = 39.764427; MAX_LAT = 40.033227
MIN_LNG = 116.214834; MAX_LNG = 116.562834
LAT_DELTA = 0.0084; LNG_DELTA = 0.012

N_LAT = int(math.ceil((MAX_LAT - MIN_LAT) / LAT_DELTA))
N_LNG = int(math.ceil((MAX_LNG - MIN_LNG) / LNG_DELTA))

LNG_COORDINATES = [MIN_LNG + i_LNG * LNG_DELTA for i_LNG in range(N_LNG + 1)]
LAT_COORDINATES = [MIN_LAT + i_LAT * LAT_DELTA for i_LAT in range(N_LAT + 1)]

def read_origin_data_into_geo_point_list(input_file_path, sep="\t",line_end = "\n", max_lines = -1):
    geo_points_List = []
    geo_time_dict = {}
    line_counter = 0
    with open(input_file_path, "r") as input_file:
        line = input_file.readline()
        while line:
            line_counter += 1
            if max_lines > 0 and line_counter > max_lines:
                break
            line_contents = line.strip(line_end).split(sep)
            time_of_point = datetime.datetime.strptime(line_contents[1], SECOND_FORMAT)

            time_str = time_of_point.strftime("%Y-%m-%d %H:%M:%S")
            geo_time_dict[time_str] = line_counter - 1

            longtitude = float(line_contents[2])
            latitude = float(line_contents[3])
            geo_point = [time_of_point, longtitude, latitude]
            geo_points_List.append(geo_point)
            line = input_file.readline()
    return [geo_points_List, geo_time_dict]


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
