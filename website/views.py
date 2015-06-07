from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User
from django.db.models import Q
from itertools import chain

import json
import time
import logging
import traceback

import favit.models
import query
import models
import sql_manager

from ml.models import machine_learning_model
from date_time_encoder import DateTimeEncoder

logger = logging.getLogger(__name__)


@login_required
def index(request):
    if request.GET.get('q', None) is not None \
            and request.GET.get('q', None) != '':
        filter = request.GET.get('q', None)
        query_list = models.Query.objects.filter(hide_index=0).filter(
            Q(title__contains=filter) |
            Q(description__contains=filter)
        ).distinct()
        query_list2 = models.Query.objects.filter(hide_index=0).filter(
            tags__name__in=[filter]
        ).distinct()
        query_list = list(chain(query_list, query_list2))
        dashboard_list = models.Dashboard.objects.filter(hide_index=0).filter(
            Q(title__contains=filter) |
            Q(description__contains=filter)
        ).distinct()
        dashboard_list2 = models.Dashboard.objects.filter(hide_index=0).filter(
            tags__name__in=[filter]
        ).distinct()
        dashboard_list = list(chain(dashboard_list, dashboard_list2))
    elif request.GET.get('tags', None) is not None:
        # Tag search
        filter = request.GET.get('tags', None)
        query_list = models.Query.objects.filter(hide_index=0).filter(
            tags__name__in=[filter]
        ).distinct()
        dashboard_list = models.Dashboard.objects.filter(hide_index=0).filter(
            tags__name__in=[filter]
        ).distinct()
    else:
        query_list = models.Query.objects.filter(hide_index=0)
        dashboard_list = models.Dashboard.objects.filter(hide_index=0)

    # Get Favorites
    user = User.objects.get(username=request.user)
    query_favorites = favit.models.Favorite.objects.\
        for_user(user, model=models.Query)
    query_fav_dict = {}
    query_fav_dict = dict([(i.target_object_id, i) for i in query_favorites])
    query_list_images = []
    for q in query_list:
        if q.id in query_fav_dict:
            setattr(q, 'fav', True)
        else:
            setattr(q, 'fav', False)
        if q.image is not None and q.image != '':
            logging.warning(q)
            #logging.warning(q.image)
            query_list_images.append(q)

    dash_favorites = favit.models.Favorite.objects.\
        for_user(user, model=models.Dashboard)
    dash_fav_dict = dict([(i.target_object_id, i) for i in dash_favorites])

    for d in dashboard_list:
        if d.id in dash_fav_dict:
            setattr(d, 'fav', True)
        else:
            setattr(d, 'fav', False)

    return render_to_response(
        'website/index.html',
        {
            'query_list': query_list,
            'query_list_images': query_list_images,
            'dashboard_list': dashboard_list,
            'query_favorites': query_fav_dict
        },
        context_instance=RequestContext(request))


@login_required
def query_api(request, query_id):
    try:
        start_time = time.time()
        lq = query.LoadQuery(
            query_id=query_id,
            user=request.user,
            parameters=request.GET.dict(),
            cacheable=request.GET.get('cacheable', None)
        )
        q = lq.prepare_query()
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
def query_view(request, query_ids, type='query', **kwargs):
    query_id_array = query_ids.split(',')
    # TODO filter to make sure only this applies to queries which exist
    query_list = [m for m in models.Query.objects.filter(
        id__in=query_id_array)]
    # Get Favorites
    # TODO get rid of copy paste job here with queries
    user = User.objects.get(username=request.user)
    query_favorites = favit.models.Favorite.objects.for_user(
        user, model=models.Query)
    query_fav_dict = dict([(i.target_object_id, i) for i in query_favorites])

    replacement_dict = {}
    json_get = {}
    for q in query_list:
        if q.id in query_fav_dict:
            setattr(q, 'fav', True)
        else:
            setattr(q, 'fav', False)

        lq = query.LoadQuery(
            query_id=q.id,
            user=request.user,
            parameters=request.GET.dict())
        ml = machine_learning_model.objects.filter(query=q.id)
        if ml is not None:
            setattr(q, 'ml', ml)
        lq.prepare_query()
        q.query_text = lq.query.query_text
        for k, v in lq.target_parameters.iteritems():
            # This dict has target, replacement, and data_type
            replacement_dict[k] = v
            json_get[v['search_for']] = v['replace_with']
        # Add on requests for Cacheable / other needed parameters
        json_get_extra_array = ['cacheable']
        for k in json_get_extra_array:
            if request.GET.get(k, None) is not None:
                json_get[k] = request.GET.get(k)
        d = {
            'query_list': query_list,
            'replacement_dict': replacement_dict,
            'json_get': json.dumps(json_get),
            'type': type
        }
        d.update(**kwargs)
        # logging.warning(d)
    return render_to_response(
        'website/query.html',
        d,
        context_instance=RequestContext(request))


@login_required
def query_name(request, query_names):
    query_name_array = query_names.split(',')
    queries = models.Query.objects.filter(title__in=query_name_array)
    query_list_string = ','.join([str(q.id) for q in queries])
    return query_view(request, query_list_string, 'query')


@login_required
def dashboard(request, dashboard_id):
    # First find all the queries, then run it as a list of queries
    dashboard_query_list = models.DashboardQuery.objects.filter(
        dashboard_id=dashboard_id).order_by('order')
    dashboard_data = models.Dashboard.objects.filter(
        id=dashboard_id).first()
    query_id_array = []
    for q in dashboard_query_list:
        query_id_array.append(str(q.query_id))
    query_list_string = ','.join(query_id_array)
    return query_view(
        request,
        query_list_string,
        'dashboard',
        dashboard=dashboard_data)


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
        pivot = request.POST.get('pivot', '').lower() == 'true'
        cumulative = request.POST.get('cumulative', '').lower() == 'true'
        start_time = time.time()
        md = query.ManipulateData(
            query_text=query_text,
            db=db,
            user=request.user,
            cacheable=False,
        )
        md.prepare_safety()
        md.run_query()
        if pivot:
            md.pivot()
        if cumulative:
            md.cumulative()
        md.pandas_to_array()
        response_data = md.data_array  # numericalize_data_array()
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
            raise ValueError("""Database cannot be explorered yet.
                    Only supported types are MySQL &Postgres""")

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
        response_data = dmm.RQ.data_array  # numericalize_data_array()
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

"""
@login_requiredclass ArticleListView(ListView):

    model = Article

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context"""
