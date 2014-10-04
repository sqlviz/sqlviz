from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.utils import timezone
from django.views import generic
from django.template import RequestContext
from models import Query, DashboardQuery, Dashboard, QueryDefault, Db
import json
from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from query import DataManager
import time
import datetime
import logging
import sys
import traceback

logger = logging.getLogger(__name__)

def index(request, filter= None):
    if filter == None:
        query_list = Query.objects.filter(hide_index = 0)
        dashboard_list = Dashboard.objects.filter(hide_index = 0)
    else:
        query_list = Query.objects.filter(hide_index = 0).filter(tags__name__in=[filter]).distinct()
        dashboard_list = Dashboard.objects.filter(hide_index = 0).filter(tags__name__in=[filter]).distinct()
    return render_to_response('website/index.html', {'query_list': query_list, 'dashboard_list' : dashboard_list})

def query_api(request, query_id):
    try:
        startTime = time.time()
        DM = DataManager(query_id, request)
        DM.prepareQuery()
        response_data = DM.runQuery()
        try:
            DM.saveToSQLTable()
        except Exception:
            logging.warning(sys.exc_info())
        time_elapsed = time.time()-startTime
        return_data = {
                        "data":
                            {"columns" : response_data.pop(0), "data" : response_data},
                        "time_elapsed" : time_elapsed,
                        "error" : False}
    except Exception, e:
            #logging.warning(str(sys.exc_info()) + str(e))
            logging.warning(traceback.format_exc())
            return_data = {
                            "data": #'\n'.join(map
                                str(traceback.format_exc()),
                            "time_elapsed" : 0,
                            "error" : True,
                        }
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
    return render_to_response('website/query.html', 
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

def query_interactive(request):
    # Render empty page for users to add data to
    db_list = Db.objects.all()
    return render_to_response('website/query_interactive.html',{
            'db_list': db_list},
            RequestContext(request))

def query_interactive_api(request):
    # Take Query, Database, and Pivot
    # Create DataManager, run and return as JSON schema
    try:
        query_text  = request.POST['query_text']
        db  = request.POST['db']
        pivot  =  True if request.POST['pivot'].lower() == 'true' else False
        startTime = time.time()
        DM = DataManager()
        DM.setQuery(query_text)
        DM.setDB(db)
        DM.setPivot(pivot)
        response_data = DM.runQuery()
        time_elapsed = time.time() - startTime # TODO get rid of this copy-pasta
        return_data = {
                        "data":
                            {"columns" : response_data.pop(0), "data" : response_data},
                        "time_elapsed" : time_elapsed,
                        "error" : False}
    except Exception, e:
            logging.warning(traceback.format_exc())
            return_data = {
                            "data": #'\n'.join(map
                                str(traceback.format_exc()),
                            "time_elapsed" : 0,
                            "error" : True,
                        }
    return HttpResponse(json.dumps(return_data, cls = DateTimeEncoder), 
            content_type="application/json")                        

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
