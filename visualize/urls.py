from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

urlpatterns = patterns('visualize.views',
                       url(r'^index$','index',name='index'),
                       url(r'^timeline', 'timeline', name='timeline'),
                       url(r'^gtl','grid_timeline',name='grid_timeline'),
                       )