from django.conf.urls import patterns, include, url
from django.contrib import admin
# from django.views.generic.base import RedirectView
from django.conf import settings

admin.site.site_header = 'SQLViz Admin'
admin.site.index_title = ''


urlpatterns = patterns(
    '',
    url(r'^', include('website.urls', namespace='website')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^favs/', include('favs.urls', namespace='favs')),
    url(r'^', include('ml.urls', namespace='ml')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^search/', include('haystack.urls')),
)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns(
        'django.views.static',
        (
            r'media/(?P<path>.*)',
            'serve',
            {'document_root': settings.MEDIA_ROOT}
        ),
    )
