from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

urlpatterns = patterns('visualize.views',
                       url(r'^index$','index',name='index'),
                       url(r'^timeline', 'timeline', name='timeline'),
                       url(r'^gtl','grid_timeline',name='grid_timeline'),
                       url(r'^ftl','freqency_timeline',name='freqency_timeline'),
                       url(r'^prc','predict_result_comparision',name='predict_result_comparision'),
                       url(r'^query_status','query_status',name='query_status'),
                       )