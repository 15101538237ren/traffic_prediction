# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import JsonResponse
from traffic_prediction.base import *
from traffic_prediction.helpers import *
from data_processing.preprocessing import *

import simplejson

# Create your views here.

def index(request):
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

def timeline(request):
    dt_list, _ = generate_timelist(settings.START_TIME, settings.END_TIME, settings.MINUTES_INTERVAL)
    dt_list = [item.strftime(SECOND_FORMAT) for item in dt_list]
    dt_start = settings.START_TIME.strftime(SECOND_FORMAT)
    slider_cnts = len(dt_list)
    return render_to_response('timeline.html', locals(), context_instance=RequestContext(request))

def grid_timeline(request):
    if request.method == 'GET':
        dt_list,_ = generate_timelist(settings.START_TIME, settings.END_TIME, settings.MINUTES_INTERVAL)
        dt_list = [item.strftime(SECOND_FORMAT) for item in dt_list]
        dt_start = settings.START_TIME.strftime(SECOND_FORMAT)
        slider_cnts = len(dt_list)
        return render_to_response('grid_timeline.html', locals(), context_instance=RequestContext(request))
    else:
        datetime_query = request.POST.get("query_dt", settings.START_TIME.strftime(SECOND_FORMAT))
        from_dt = datetime.datetime.strptime(datetime_query, SECOND_FORMAT)
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
        time_segment = base.TIME_SEGMENTS_LABELS
        date_start = settings.START_TIME
        return render_to_response('freqency_timeline.html', locals(), context_instance=RequestContext(request))
    else:
        time_period_selected = int(request.POST.get("time_period", '7'))
        time_segment_selected = int(request.POST.get("time_segment", '0'))
        return_dict = {}
        return_dict['datetime_list'], _ = generate_timelist(settings.START_TIME, settings.END_TIME, datetime.timedelta(days=time_period_selected))
        return_dict['slider_cnts'] = len(return_dict['datetime_list'])
        return_dict['grid_boundaries'] = GRID_LNG_LAT_COORDS
        freq_matrix_dict, max_freq_dict,_ = obtain_frequency_matrix()
        frequency_matrix = freq_matrix_dict[datetime.timedelta(days=time_period_selected)][time_segment_selected]
        max_frequency = max_freq_dict[datetime.timedelta(days=time_period_selected)]

        return_dict['color_matrix'] = generate_color_matrix(frequency_matrix, max_frequency)

        json_fp = settings.os.path.join(settings.JSON_DIR, "freq_matrix.json")
        with open(json_fp,"w") as json_file:
            json_str = simplejson.dumps(return_dict, cls=DatetimeJSONEncoder)
            json_file.write(json_str)
            print ("dump %s sucessful!" % json_fp)
        addr = '/static/json/freq_matrix.json'

        response_dict = {}
        response_dict["code"] = 0
        response_dict["addr"] = addr

        return JsonResponse(response_dict)

def predict_result_comparision(request):
    if request.method == 'GET':
        time_period = settings.TIME_PERIODS
        time_segment = base.TIME_SEGMENTS_LABELS
        classifier_names = base.classifier_names
        seq_lens = base.SEQUENCE_LENGTHS
        date_start = settings.START_TIME
        return render_to_response('predict_result_comparision.html', locals(), context_instance=RequestContext(request))
    else:
        time_period_selected = int(request.POST.get("time_period", '7'))
        time_segment_selected = int(request.POST.get("time_segment", '0'))
        classifier_name_selected = request.POST.get("classifier_name", 'lstm')
        seq_len_selected = int(request.POST.get("seq_len", '19'))
        datetime_list, frequency_matrix_real, frequency_matrix_predicted, max_frequency, _ , _, _ = load_prediction_result(time_period_selected, time_segment_selected, classifier_name_selected, seq_len_selected)

        return_dict = {}
        return_dict['datetime_list'] = datetime_list
        return_dict['slider_cnts'] = len(datetime_list)
        return_dict['grid_boundaries'] = GRID_LNG_LAT_COORDS
        return_dict['color_matrix_real'] = generate_color_matrix(frequency_matrix_real, max_frequency)
        return_dict['color_matrix_predicted'] = generate_color_matrix(frequency_matrix_predicted, max_frequency)
        name_of_json_file = 'predict_result_comparision.json'

        json_fp = settings.os.path.join(settings.JSON_DIR, name_of_json_file)
        with open(json_fp, "w") as json_file:
            json_str = simplejson.dumps(return_dict, cls=DatetimeJSONEncoder)
            json_file.write(json_str)
            print ("dump %s sucessful!" % json_fp)
        addr = '/static/json/' + name_of_json_file

        response_dict = {}
        response_dict["code"] = 0
        response_dict["addr"] = addr

        return JsonResponse(response_dict)

def params(request):
    classifier_names = base.classifier_names
    lstm_layers = [4, 3, 2, 1]
    fc_nn_layers = [4, 3, 2, 1]
    n_neurons = [1000, 500, 200, 100]
    time_period = settings.TIME_PERIODS
    time_segment = base.TIME_SEGMENTS_LABELS
    seq_lens = base.SEQUENCE_LENGTHS
    date_start = settings.START_TIME
    return render_to_response('params.html', locals(), context_instance=RequestContext(request))

def predicted_line_chart(request):
    if request.method == 'GET':
        time_period = settings.TIME_PERIODS
        time_segment = base.TIME_SEGMENTS_LABELS
        classifier_names = base.classifier_names
        seq_lens = base.SEQUENCE_LENGTHS
        date_start = settings.START_TIME
        return render_to_response('predicted_line_chart.html', locals(), context_instance=RequestContext(request))
    else:
        time_period_selected = int(request.POST.get("time_period", '7'))
        time_segment_selected = int(request.POST.get("time_segment", '0'))
        classifier_name_selected = request.POST.get("classifier_name", 'lstm')
        seq_len_selected = int(request.POST.get("seq_len", '19'))
        ret_dict = {'grid_boundaries': GRID_LNG_LAT_COORDS}
        _, _, _, _, ret_dict['datetime_str_list'], ret_dict['real_frequency'], ret_dict['predicted_frequency'] = load_prediction_result(time_period_selected, time_segment_selected, classifier_name_selected, seq_len_selected)

        name_of_json_file = "predicted_line_chart.json"
        json_fp = settings.os.path.join(settings.JSON_DIR, name_of_json_file)

        with open(json_fp, "w") as json_file:
            json_str = simplejson.dumps(ret_dict)
            json_file.write(json_str)
            print ("dump %s sucessful!" % json_fp)

        addr = '/static/json/' + name_of_json_file
        response_dict = {}
        response_dict["code"] = 0
        response_dict["addr"] = addr
        option_addr = '/static/json/line_chart_option.json'
        response_dict["option_addr"] = option_addr
        return JsonResponse(response_dict)
@ajax_required
def query_status(request):
    datetime_query = request.POST.get("query_dt", settings.START_TIME.strftime(SECOND_FORMAT))

    from_dt = datetime.datetime.strptime(datetime_query, SECOND_FORMAT)
    end_dt = from_dt + settings.MINUTES_INTERVAL
    geo_points_list_tmp, _ = obtain_origin_data()
    get_geo_points_from(geo_points_list_tmp, from_dt, end_dt, write=True)
    addr = '/static/json/geo_points.json'
    response_dict = {}
    response_dict["code"] = 0
    response_dict["addr"] = addr
    return JsonResponse(response_dict)