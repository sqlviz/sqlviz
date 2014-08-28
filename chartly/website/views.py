from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.utils import timezone
from django.views import generic
from django.template import RequestContext
from models import Query, DashboardQuery, Dashboard, QueryDefault
import json
from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from query import DataManager
import time
import datetime
import logging
logger = logging.getLogger(__name__)

def index(request):
    query_list = Query.objects.filter(hide_index = 0)
    dashboard_list = Dashboard.objects.filter(hide_index = 0)
    return render_to_response('index.html', {'query_list': query_list, 'dashboard_list' : dashboard_list})

def query_api(request, query_id):
    startTime = time.time()
    DM = DataManager(query_id, request)
    DM.prepareQuery()
    response_data = DM.runQuery()
    time_elapsed = time.time()-startTime
    return_data = {
                    "data":
                        {"columns" : response_data.pop(0), "data" : response_data},
                    "time_elapsed" : time_elapsed,
                    "error" : False}
    return HttpResponse(json.dumps(return_data, cls = DateTimeEncoder), content_type="application/json")

def query(request, query_ids):
    # TODO display in the order that they come in!!!
    query_id_array = query_ids.split(',')
    query_list = Query.objects.filter(id__in = query_id_array)
    replacement_dict = {}
    json_get = {}
    for query in query_list:
        DM = DataManager(query.id, request)
        DM.prepareQuery()
        query.query_text = DM.query_text
        for k,v in DM.replacement_dict.iteritems():
            replacement_dict[k] = v # This dict has target, replacement, and data_type
            json_get[v['search_for']] = v['replace_with']
    #logging.warning(request.get)
    return render_to_response('query.html', 
                {
                    'query_list': query_list,
                    'replacement_dict' : replacement_dict,
                    'json_get' : json.dumps(json_get)
                },
                context_instance=RequestContext(request))
    
def query_name(request, query_names):
    query_name_array = query_names.split(',')
    query_list = Query.objects.filter(title__in = query_name_array)
    query_id_array = []
    for q in query_list:
        query_id_array.append(str(q.id))
    query_list_string  = ','.join(query_id_array)
    return query(request, query_list_string)

def dashboard(request, dashboard_id):
    # First find all the queries, then run it as a list of queries
    dashboard_query_list = DashboardQuery.objects.filter(dashboard_id = dashboard_id).order_by('order')
    query_id_array = []
    for q in dashboard_query_list:
        query_id_array.append(str(q.query_id))
    query_list_string  = ','.join(query_id_array)
    return query(request, query_list_string)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        else:
            return super(DateTimeEncoder, self).default(obj)
