from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'chartly.views.home', name='home'),
   	url(r'^', include('website.urls', namespace="website")),
	url(r'^website/', include('website.urls', namespace="website")),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^accounts/', include('accounts.urls'), name='accounts')
)
