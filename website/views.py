from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User
from django.db.models import Q

import json
import time
import logging
import traceback

import favit.models
import query
import models
import sql_manager
from date_time_encoder import DateTimeEncoder

logger = logging.getLogger(__name__)


@login_required
def index(request):
    if request.GET.get('q', None) is None:
        query_list = models.Query.objects.filter(hide_index=0)
        dashboard_list = models.Dashboard.objects.filter(hide_index=0)
    else:
        filter = request.GET.get('q', None)
        query_list = models.Query.objects.filter(hide_index=0).filter(Q(title__contains=filter) | Q(description__contains=filter)).distinct()
        dashboard_list = models.Dashboard.objects.filter(hide_index = 0).filter(Q(title__contains=filter) | Q(description__contains=filter)).distinct()

    # Get Favorites
    user = User.objects.get(username=request.user)
    query_favorites = favit.models.Favorite.objects.\
        for_user(user, model=models.Query)
    query_fav_dict = {}
    query_fav_dict = dict([(i.target_object_id, i) for i in query_favorites])
    for q in query_list:
        if q.id in query_fav_dict:
            setattr(q, 'fav', True)
        else:
            setattr(q, 'fav', False)

    dash_favorites = favit.models.Favorite.objects.\
        for_user(user, model=models.Dashboard)
    dash_fav_dict = dict([(i.target_object_id, i) for i in dash_favorites])
    # logging.warning('%s coco puffs' % (dash_fav_dict))
    for d in dashboard_list:
        if d.id in dash_fav_dict:
            setattr(d, 'fav', True)
        else:
            setattr(d, 'fav', False)

    return render_to_response(
        'website/index.html',
        {
            'query_list': query_list,
            'dashboard_list': dashboard_list,
            'query_favorites': query_fav_dict
        },
        context_instance=RequestContext(request))


@login_required
def query_api(request, query_id):
    try:
        start_time = time.time()
        LQ = query.Load_Query(
            query_id=query_id,
            user=request.user,
            parameters=request.GET.dict(),
            cacheable=request.GET.get('cacheable', None)
        )
        q = LQ.prepare_query()
        q.run_query()
        q.run_manipulations()
        response_data = q.data_array
        time_elapsed = time.time() - start_time
        # logging.warning('Cache Status View %s' % (q.get_cache_status()))
        return_data = {
            "data":
                {"columns": response_data.pop(0), "data": response_data},
            "time_elapsed": round(time_elapsed, 2),
            "cached": q.get_cache_status(),
            "error": False}
    except Exception, e:
        # logging.warning(str(sys.exc_info()) + str(e))
        logging.warning(traceback.format_exc())
        return_data = {
            "data": str(e),
            "time_elapsed": 0,
            "cached": False,
            "error": True}
    return HttpResponse(
        json.dumps(return_data, cls=DateTimeEncoder),
        content_type="application/json")


@login_required
def query_view(request, query_ids):
    query_id_array = query_ids.split(',')
    # TODO filter to make sure only this applies to queries which exist
    query_list = [m for m in models.Query.objects.filter(id__in = query_id_array)]
    # Get Favorites
    # TODO get rid of copy paste job here with queries
    user = User.objects.get(username=request.user)
    query_favorites = favit.models.Favorite.objects.for_user(user, model=models.Query)
    query_fav_dict = dict([(i.target_object_id, i) for i in query_favorites])

    replacement_dict = {}
    json_get = {}
    for q in query_list:
        if q.id in query_fav_dict:
            setattr(q, 'fav', True)
        else:
            setattr(q, 'fav', False)

        LQ = query.Load_Query(
            query_id=q.id,
            user=request.user,
            parameters=request.GET.dict())
        LQ.prepare_query()
        q.query_text = LQ.query.query_text
        for k, v in LQ.target_parameters.iteritems():
            # This dict has target, replacement, and data_type
            replacement_dict[k] = v
            json_get[v['search_for']] = v['replace_with']
        # Add on requests for Cacheable / other needed parameters
        json_get_extra_array = ['cacheable']
        for k in json_get_extra_array:
            if request.GET.get(k, None) is not None:
                json_get[k] = request.GET.get(k)
    return render_to_response(
        'website/query.html',
        {
            'query_list': query_list,
            'replacement_dict': replacement_dict,
            'json_get': json.dumps(json_get)
        },
        context_instance=RequestContext(request))

@login_required
def query_name(request, query_names):
    query_name_array = query_names.split(',')
    query_list_string = ','.join([str(m.id) for m in models.Query.objects.filter(title__in = query_name_array)])
    return query_view(request, query_list_string)


@login_required
def dashboard(request, dashboard_id):
    # First find all the queries, then run it as a list of queries
    dashboard_query_list = models.DashboardQuery.objects.filter(dashboard_id = dashboard_id).order_by('order')
    query_id_array = []
    for q in dashboard_query_list:
        query_id_array.append(str(q.query_id))
    query_list_string = ','.join(query_id_array)
    return query_view(request, query_list_string)


@login_required
def query_interactive(request):
    # Render empty page for users to add data to
    db_list = models.Db.objects.all()
    return render_to_response(
        'website/query_interactive.html',
        {'db_list': db_list},
        RequestContext(request))


@login_required
def query_interactive_api(request):
    # Take Query, Database, and Pivot
    # Create DataManager, run and return as JSON schema
    try:
        query_text = request.POST['query_text']
        db = models.Db.objects.filter(id=request.POST['db']).first()
        pivot = True if request.POST.get('pivot', '').lower() == 'true' else False
        cumulative = True if request.POST.get('cumulative', '').lower() == 'true' else False
        start_time = time.time()
        MD = query.Manipulate_Data(
            query_text=query_text,
            db=db,
            user=request.user,
            cacheable=False,
        )
        MD.prepare_safety()
        MD.run_query()
        if pivot:
            MD.pivot()
        if cumulative:
            MD.cumulative()
        MD.pandas_to_array()
        response_data = MD.numericalize_data_array()
        time_elapsed = time.time() - start_time  # TODO get rid of this
        return_data = {
            "data": {
                "columns": response_data.pop(0),
                "data": response_data
            },
            "time_elapsed": time_elapsed,
            "error": False}
    except Exception, e:
            logging.warning(traceback.format_exc())
            return_data = {
                "data": str(e),
                "time_elapsed": 0,
                "error": True}
    return HttpResponse(json.dumps(return_data, cls=DateTimeEncoder),
                        content_type="application/json")


@login_required
def database_explorer(request):
    # Render empty page for users to add data to
    db_list = models.Db.objects.all()
    return render_to_response(
        'website/database_explorer.html',
        {'db_list': db_list},
        RequestContext(request))


@login_required
def database_explorer_api(request):
    # Get DB
    try:
        con_id = request.GET.get('con_id')  # connection id is needed
        db_id = request.GET.get('db_id', None)  # Database's database or none
        table_id = request.GET.get('table_id', None)  # table name , or none
        # Get DB Type
        con = models.Db.objects.filter(id=con_id).first()

        # Switch in database Type
        if con.type == 'MySQL':
            dmm = sql_manager.MySQLManager(con, request)
        elif con.type == 'Postgres':
            dmm = sql_manager.PSQLManager(con, request)
        else:
            raise ValueError("""Database cannot be explorered yet. Only supported types are 'MySQL','Postgres'""")

        # Get proper response data
        if db_id is None:
            dmm.find_database()
        elif table_id is None:  # Show tables if table is none
            dmm.show_tables(db_id)
        elif table_id is not None:
            dmm.describe_table(db_id, table_id)
        else:
            raise ValueError("""ERROR: con_id is needed,
                    db_id needed for to produce table list,
                    table_id needed to procude column list""")

        dmm.run_query()
        response_data = dmm.RQ.numericalize_data_array()
        # logging.warning(""" BINGO %s """ % response_data)
        return_data = {
            "data":
            {
                "columns": response_data.pop(0),
                "data": response_data
            },
            "error": False}
        return HttpResponse(
            json.dumps(return_data, cls=DateTimeEncoder),
            content_type="application/json")
    except Exception:
            logging.warning(traceback.format_exc())
            return_data = {
                "data": str(traceback.format_exc()),
                "time_elapsed": 0,
                "error": True}
    return HttpResponse(
        json.dumps(return_data, cls=DateTimeEncoder),
        content_type="application/json")
