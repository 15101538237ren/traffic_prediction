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
    dt_list, _ = generate_timelist(settings.START_TIME, settings.END_TIME, settings.MINUTES_INTERVAL)
    dt_start = settings.START_TIME.strftime(SECOND_FORMAT)
    slider_cnts = len(dt_list)
    return render_to_response('timeline.html', locals(), context_instance=RequestContext(request))

def grid_timeline(request):
    if request.method == 'GET':
        dt_list,_ = generate_timelist(settings.START_TIME, settings.END_TIME, settings.MINUTES_INTERVAL)
        dt_start = settings.START_TIME.strftime(SECOND_FORMAT)
        slider_cnts = len(dt_list)
        return render_to_response('grid_timeline.html', locals(), context_instance=RequestContext(request))
    else:
        datetime_query = request.POST.get("query_dt", settings.START_TIME.strftime(SECOND_FORMAT))

        from_dt = datetime.datetime.strptime(datetime_query,SECOND_FORMAT)
        end_dt = from_dt + settings.MINUTES_INTERVAL

        out_data_file = BASE_DIR+'/static/js/grid_timeline.js'

        generate_grid_timelines_for_beijing(from_dt, end_dt, out_data_file)
        addr = '/static/js/grid_timeline.js'
        response_dict = {}
        response_dict["code"] = 0
        response_dict["addr"] = addr

        return JsonResponse(response_dict)

def freqency_timeline(request):
    target_time_segment = DAWN
    frequency_matrix = frequency_matrix_by_time_segment[target_time_segment]

    dt_list, _ = generate_timelist(settings.START_TIME, settings.END_TIME, settings.DAYS_INTERVAL)
    slider_cnts = len(dt_list)
    out_js_file = BASE_DIR+'/static/js/region.js'
    return render_to_response('freqency_timeline.html', locals(), context_instance=RequestContext(request))


@ajax_required
def query_status(request):
    datetime_query = request.POST.get("query_dt", settings.START_TIME.strftime(SECOND_FORMAT))

    from_dt = datetime.datetime.strptime(datetime_query, SECOND_FORMAT)
    end_dt = from_dt + settings.MINUTES_INTERVAL

    get_geo_points_from(from_dt, end_dt, -1, type=settings.POINT_TYPE)
    addr = '/static/points.json'
    response_dict = {}
    response_dict["code"] = 0
    response_dict["addr"] = addr
    return JsonResponse(response_dict)