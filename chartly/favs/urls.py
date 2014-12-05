from django.conf.urls import patterns, url
#from django.contrib.auth.decorators import login_required, permission_required

from views import *

urlpatterns = patterns('',
   	url(r'^api/fav/$', favorite_set_api, name='favorite_set_api')
)