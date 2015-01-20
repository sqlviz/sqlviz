# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
import simplejson
from favit.models import Favorite


@login_required
def add_or_remove(request):
    user = request.user
    try:
        app_model = request.POST["target_model"]
        obj_id = int(request.POST["target_object_id"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    fav = Favorite.objects.get_favorite(user, obj_id, model=app_model)

    if fav is None:
        Favorite.objects.create(user, obj_id, app_model)
        status = 'added'
    else:
        fav.delete()
        status = 'deleted'

    response = {
        'status': status,
        'fav_count': Favorite.objects.for_object(obj_id, app_model).count()
    }

    return HttpResponse(
        simplejson.dumps(response, ensure_ascii=False)
    )


@login_required
def add(request):
    user = request.user
    try:
        app_model = request.POST["target_model"]
        obj_id = int(request.POST["target_object_id"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    fav = Favorite.objects.get_favorite(user, obj_id, model=app_model)

    if fav is None:
        Favorite.objects.create(user, obj_id, app_model)
    status = 'added'

    response = {
        'status': status,
        'fav_count': Favorite.objects.for_object(obj_id, app_model).count()
    }

    return HttpResponse(
        simplejson.dumps(response, ensure_ascii=False)
    )


@login_required
def remove(request):
    user = request.user

    try:
        app_model = request.POST["target_model"]
        obj_id = int(request.POST["target_object_id"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    Favorite.objects.get_favorite(user, obj_id, model=app_model).delete()
    status = 'deleted'

    response = {
        'status': status,
    }

    return HttpResponse(
        simplejson.dumps(response, ensure_ascii=False)
    )
