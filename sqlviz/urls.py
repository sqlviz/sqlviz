from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = patterns('',
    url(r'^', include('website.urls', namespace='website')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^favs/', include('favs.urls', namespace = 'favs'))
 )


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('django.views.static',
        (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )
