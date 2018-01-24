from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.

def index(request):
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

def timeline(request):
    return render_to_response('timeline.html', locals(), context_instance=RequestContext(request))

def grid_timeline(request):
    return render_to_response('grid_timeline.html', locals(), context_instance=RequestContext(request))