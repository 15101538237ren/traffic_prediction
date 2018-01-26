# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import JsonResponse
from traffic_prediction.base import *
from data_processing.preprocessing import *

# Create your views here.

def index(request):
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

def timeline(request):
    start_time = datetime.datetime.strptime("2016-05-04 18:00:00", SECOND_FORMAT)
    end_time = datetime.datetime.strptime("2016-05-20 15:00:00", SECOND_FORMAT)
    time_interval = 30
    dt_list = get_all_datetimes(start_time, end_time, time_interval=time_interval)
    dt_start = start_time.strftime(SECOND_FORMAT)
    slider_cnts = len(dt_list)
    print slider_cnts
    return render_to_response('timeline.html', locals(), context_instance=RequestContext(request))

def grid_timeline(request):
    time_interval = 30
    sep = 1000
    if request.method == 'GET':
        start_time = datetime.datetime.strptime("2016-05-04 18:00:00",SECOND_FORMAT)
        end_time = datetime.datetime.strptime("2016-05-04 18:23:00",SECOND_FORMAT)
        dt_list = get_all_datetimes(start_time,end_time,time_interval=time_interval)
        dt_start = start_time.strftime(SECOND_FORMAT)
        slider_cnts = len(dt_list)
        return render_to_response('prep/grid_timeline.html', locals(), context_instance=RequestContext(request))
    else:
        datetime_query = request.POST.get("query_dt","2016-05-04 18:00:00")
        from_dt = datetime.datetime.strptime(datetime_query,SECOND_FORMAT)
        end_dt = from_dt + datetime.timedelta(minutes=time_interval)

        out_data_file = BASE_DIR+'/static/js/grid_timeline.js'

        min_lat,max_lat,min_lng,max_lng = get_grid_timeline(datetime_query,out_data_file, sep= sep,time_interval = time_interval)
        addr = '/static/grid_timeline.js'
        response_dict = {}
        response_dict["code"] = 0
        response_dict["addr"] = addr
        return JsonResponse(response_dict)

@ajax_required
def query_status(request):
    time_interval = 30
    datetime_query = request.POST.get("query_dt","2016-05-04 18:00:00")
    from_dt = datetime.datetime.strptime(datetime_query,SECOND_FORMAT)
    end_dt = from_dt + datetime.timedelta(minutes=time_interval)
    get_geo_points_from(from_dt, end_dt, type="violation")
    addr = '/static/points.json'
    response_dict = {}
    response_dict["code"] = 0
    response_dict["addr"] = addr
    return JsonResponse(response_dict)