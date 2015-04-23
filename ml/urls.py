from django.conf.urls import patterns, url

from views import *
# build_model, build_model_adhoc, use_model, view_model, index

urlpatterns = patterns('',
                       url(r'^api/ml/build/(?P<ml_id>\d+)/$',
                           build_model, name='build_model'),
                       url(r'^api/ml/build/$',
                           build_model_adhoc, name='build_model_adhoc'),
                       url(r'^api/ml/(?P<ml_id>\d+)/use/$',
                           use_model, name='use_model'),
                       url(r'^/ml/(?P<ml_id>\d+)$',
                           view_model, name='view_model'),
                       url(r'^ml/',
                           index, name='index')
                       )
