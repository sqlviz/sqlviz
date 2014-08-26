from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.utils import timezone
from django.views import generic
from models import Query, DashboardQuery, Dashboard
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
    DM = DataManager(query_id)
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
    query_id_array = query_ids.split(',')
    query_list = Query.objects.filter(id__in = query_id_array)
    return render_to_response('query.html', {'query_list': query_list})

def dashboard(request, dashboard_id):
    dashboard_query_list = DashboardQuery.objects.filter(dashboard_id = dashboard_id).order_by('order')
    logging.warning(dashboard_query_list)
    query_id_array = []
    for q in dashboard_query_list:
        query_id_array.append(q.query_id)
    query_list = Query.objects.filter(id__in = query_id_array)
    return render_to_response('query.html', {'query_list': query_list})

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
