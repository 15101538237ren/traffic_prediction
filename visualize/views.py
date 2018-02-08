# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import JsonResponse
from traffic_prediction.base import *
from data_processing.preprocessing import *
import simplejson

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
    if request.method == 'GET':
        time_period = settings.TIME_PERIODS
        time_segment = settings.TIME_SEGMENTS
        date_start = settings.START_TIME
        return render_to_response('freqency_timeline.html', locals(), context_instance=RequestContext(request))
    else:
        time_period_selected = int(request.POST.get("time_period", '7'))
        time_segment_selected = int(request.POST.get("time_segment", '0'))
        return_dict = {}
        return_dict['datetime_list'], _ = generate_timelist(settings.START_TIME, settings.END_TIME, datetime.timedelta(days=time_period_selected))
        return_dict['slider_cnts'] = len(return_dict['datetime_list'])
        frequency_matrix = frequency_matrix_dict[datetime.timedelta(days=time_period_selected)][time_segment_selected]
        max_frequency = max_frequency_dict[datetime.timedelta(days=time_period_selected)]


        json_fp = settings.os.path.join(settings.JSON_DIR, "freq_matrix.json")
        with open(json_fp,"w") as json_file:
            json_str = simplejson.dumps(return_dict, cls=base.DatetimeJSONEncoder)
            json_file.write(json_str)
            print "dump %s sucessful!" % json_fp
        addr = '/static/json/freq_matrix.json'

        response_dict = {}
        response_dict["code"] = 0
        response_dict["addr"] = addr

        return JsonResponse(response_dict)


@ajax_required
def query_status(request):
    datetime_query = request.POST.get("query_dt", settings.START_TIME.strftime(SECOND_FORMAT))

    from_dt = datetime.datetime.strptime(datetime_query, SECOND_FORMAT)
    end_dt = from_dt + settings.MINUTES_INTERVAL

    get_geo_points_from(from_dt, end_dt, -1, type=settings.POINT_TYPE)
    addr = '/static/json/geo_points.json'
    response_dict = {}
    response_dict["code"] = 0
    response_dict["addr"] = addr
    return JsonResponse(response_dict)