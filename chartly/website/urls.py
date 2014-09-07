from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, permission_required

from views import *

urlpatterns = patterns('',
   	url(r'^$', login_required(index), name='home'),
   	url(r'^query_api/(?P<query_id>\d+)$', query_api, name='query_api'),
   	url(r'^query/(?P<query_ids>[,\w]+)$', query, name='query'),
   	url(r'^query/(?P<query_names>[\w\ ]+)$', query_name, name='query_name'),
   	url(r'^dashboard/(?P<dashboard_id>\d+)$', dashboard, name='dashboard'),
   	url(r'^main/(?P<filter>[\w\ ]+)$', index, name='filter'),
   	url(r'^query_interactive/', query_interactive, name='query_interactive')
)