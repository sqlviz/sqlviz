from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.utils import timezone
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import models
import json
from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
import query
import time
import datetime
import logging
import sys
import traceback

logger = logging.getLogger(__name__)

@login_required
def index(request, filter= None):
    if filter == None:
        query_list = models.Query.objects.filter(hide_index = 0)
        dashboard_list = models.Dashboard.objects.filter(hide_index = 0)
    else:
        query_list = models.Query.objects.filter(hide_index = 0).filter(tags__name__in=[filter]).distinct()
        dashboard_list = models.Dashboard.objects.filter(hide_index = 0).filter(tags__name__in=[filter]).distinct()
    return render_to_response('website/index.html',
            {'query_list': query_list, 'dashboard_list' : dashboard_list},
            context_instance = RequestContext(request))

@login_required
def query_api(request, query_id):
    try:
        startTime = time.time()
        DM = query.DataManager(query_id, request)
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

@login_required
def query_view(request, query_ids):
    query_id_array = query_ids.split(',')
    #TODO filter to make sure only this applies to queries which exist
    query_list = [models.Query.objects.filter(id = i)[0] for i in query_id_array]
    logging.warning(query_id_array)
    logging.warning(query_list)
    replacement_dict = {}
    json_get = {}
    for q in query_list:
        DM = query.DataManager(q.id, request)
        DM.prepareQuery()
        q.query_text = DM.query_text
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

@login_required    
def query_name(request, query_names):
    query_name_array = query_names.split(',')
    c
    query_id_array = []
    for q in query_list:
        query_id_array.append(str(q.id))
    query_list_string  = ','.join(query_id_array)
    return query_view(request, query_list_string)

@login_required
def dashboard(request, dashboard_id):
    # First find all the queries, then run it as a list of queries
    dashboard_query_list = models.DashboardQuery.objects.filter(dashboard_id = dashboard_id).order_by('order')
    query_id_array = []
    for q in dashboard_query_list:
        query_id_array.append(str(q.query_id))
    query_list_string  = ','.join(query_id_array)
    return query_view(request, query_list_string)

@login_required
def query_interactive(request):
    # Render empty page for users to add data to
    db_list = models.Db.objects.all()
    return render_to_response('website/query_interactive.html',{
            'db_list': db_list},
            RequestContext(request))
@login_required
def query_interactive_api(request):
    # Take Query, Database, and Pivot
    # Create DataManager, run and return as JSON schema
    try:
        query_text  = request.POST['query_text']
        db  = request.POST['db']
        pivot  =  True if request.POST['pivot'].lower() == 'true' else False
        cumulative  =  True if request.POST['cumulative'].lower() == 'true' else False
        startTime = time.time()
        DM = query.DataManager()
        DM.setQuery(query_text)
        DM.setDB(db)
        DM.setPivot(pivot)
        DM.setCumulative(cumulative)
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

@login_required
def database_explorer(request):
    # Render empty page for users to add data to
    db_list = models.Db.objects.all()
    return render_to_response('website/database_explorer.html',{
            'db_list': db_list},
            RequestContext(request))

@login_required
def database_explorer_api(request):
    # Get DB
    try:
        con_id = request.GET.get('con_id') # connection id is needed
        db_id = request.GET.get('db_id',None) # Database's database or none
        table_id = request.GET.get('table_id',None) # table name , or none
        # Get DB Type
        con = models.Db.objects.filter(id = con_id).first()
        
        # Switch in database Type
        if con.type == 'MySQL':
            DMM = query.MySQLManager(con)
        elif con.type == 'Postgres':
            DMM = query.PSQLManager(con)
        else:
            raise ValueError("Database cannot be explorered yet only supported types are 'MySQL','Postgres'")

        # Get proper response data
        if db_id is None:
            DMM.findDatabase()
        elif table_id is None: # Show tables if table is none
            DMM.showTables(db_id)
        elif table_id is not None:
            DMM.describeTable(db_id, table_id)
        else:
            raise ValueError("""ERROR: con_id is needed,
                    db_id needed for to produce table list,
                    table_id needed to procude column list""")
        response_data = DMM.runQuery()
        return_data = {
                "data":
                    {"columns" : response_data.pop(0), "data" : response_data},
                "error" : False}    
        return HttpResponse(json.dumps(return_data, cls = DateTimeEncoder), 
                content_type="application/json")
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
