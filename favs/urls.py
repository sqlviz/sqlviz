from django.conf.urls import patterns, url

urlpatterns = patterns('favs.views',
    url(r'^add-or-remove$', 'add_or_remove',name='add_or_remove'),
    url(r'^add$', 'add',name='add'),
    url(r'^remove$', 'remove', name='remove'),
)
