from django.conf.urls import patterns, url

from views import build_model, use_model, view_model, index

urlpatterns = patterns('',
                       url(r'^api/ml/(?P<ml_id>\d+)/build/$',
                           build_model, name='build_model'),
                       url(r'^api/ml/(?P<ml_id>\d+)/use/$',
                           use_model, name='use_model'),
                       url(r'^/ml/(?P<ml_id>\d+)$',
                           view_model, name='view_model'),
                       url(r'^ml/',
                           index, name='index')
                       )
