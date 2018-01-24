import os, datetime, math
from traffic_prediction import settings

data_dir = os.path.join(settings.BASE_DIR, "data")
origin_dir = os.path.join(data_dir, "origin")

SECOND_FORMAT = "%Y-%m-%d %H:%M:%S"

DAWN = 0; MORNING_RUSH = 1; MORNING_WORKING = 2; NOON = 3; AFTERNOON = 4; NIGHT = 5

MIN_LAT = 39.764427; MAX_LAT = 40.033227
MIN_LNG = 116.214834; MAX_LNG = 116.562834
LAT_DELTA = 0.0084; LNG_DELTA = 0.012

N_LAT = int(math.ceil((MAX_LAT - MIN_LAT) / LAT_DELTA))
N_LNG = int(math.ceil((MAX_LNG - MIN_LNG) / LNG_DELTA))

LNG_COORDINATES = [MIN_LNG + i_LNG * LNG_DELTA for i_LNG in range(N_LNG + 1)]
LAT_COORDINATES = [MIN_LAT + i_LAT * LAT_DELTA for i_LAT in range(N_LAT + 1)]

def read_origin_data_into_geo_point_list(input_file_path, sep="\t",line_end = "\n"):
    geo_points_List = []
    with open(input_file_path, "r") as input_file:
        line = input_file.readline()
        while line:
            line_contents = line.strip(line_end).split(sep)
            time_of_point = datetime.datetime.strptime(line_contents[1], SECOND_FORMAT)
            longtitude = float(line_contents[2])
            latitude = float(line_contents[2])
            geo_point = [time_of_point, longtitude, latitude]
            geo_points_List.append(geo_point)
            line = input_file.readline()
    return geo_points_List