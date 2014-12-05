from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User

import json
import logging
import traceback

import models
import website.models
import favit

# Create your views here.

@login_required
def favorite_set_api(request):
    """
    check if item is  a query or a dashboard
    and sets to the requested state
    """
    logging.warning(dir(favit))
    if True:
    #try:
        fav_type = request.GET.get('type')
        id = request.GET.get('id')
        state = request.GET.get('state')
        user = User.objects.get(username = request.user)
        if fav_type == 'Q':
            query = website.models.Query.objects.get(pk=id)
            fav = favit.models.Favorite.objects.remove(user, query)
                Favorite.objects.get_favorite(user, obj_id, model=app_model).delete()

        elif fav_type == 'D':
            dash = website.models.Dashboard.objects.get(pk=id)
            fav = favit.models.Favorite.objects.remove(user, dash)
        else:
            raise ValueError('%s is not known data type' % fav_type)
        
        if state == 1: # Add
            fav.save()
        elif state == 0: # remove       
            fav.delete()
        else:
            raise ValueError('%s is not known state type' % state)
        return_data = {'state' : state, 'state' : state, "error" : False}
    """except Exception, e:
        logging.warning(traceback.format_exc())
        return_data = {
                        "data": #str(traceback.format_exc()),
                        str(e)
                    }"""
    return HttpResponse(json.dumps(return_data), content_type="application/json")