from django.conf.urls import include, url, patterns
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = patterns('visualize.views',
                       url(r'^index$','index',name='index'),
                       url(r'^timeline', 'timeline', name='timeline'),
                       url(r'^gtl','grid_timeline',name='grid_timeline'),
                       url(r'^ftl','freqency_timeline',name='freqency_timeline'),
                       url(r'^plc','predicted_line_chart',name='predicted_line_chart'),
                       url(r'^prc','predict_result_comparision',name='predict_result_comparision'),
                       url(r'^params','params',name='params'),
                       url(r'^query_status','query_status',name='query_status'),
                       )

# urlpatterns = ['visualize.views',
#                        url(r'^index$','index',name='index'),
#                        url(r'^timeline', 'timeline', name='timeline'),
#                        url(r'^gtl','grid_timeline',name='grid_timeline'),
#                        url(r'^ftl','freqency_timeline',name='freqency_timeline'),
#                        url(r'^plc','predicted_line_chart',name='predicted_line_chart'),
#                        url(r'^prc','predict_result_comparision',name='predict_result_comparision'),
#                        url(r'^query_status','query_status',name='query_status'),
# ]