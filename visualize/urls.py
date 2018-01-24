from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

urlpatterns = patterns('visualize.views',
                       url(r'^index$','index',name='index'),
                       )