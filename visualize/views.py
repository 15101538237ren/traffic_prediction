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
    return render_to_response('grid_timeline.html', locals(), context_instance=RequestContext(request))

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