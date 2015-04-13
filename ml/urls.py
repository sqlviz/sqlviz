from django.conf.urls import patterns, url

from views import build_model, use_model

urlpatterns = patterns('',
                       url(r'^api/ml/(?P<ml_id>\d+)/build/$',
                           build_model, name='ml_id'),
                       url(r'^api/ml/(?P<ml_id>\d+)/use/$',
                           use_model, name='ml_id')
                       )
