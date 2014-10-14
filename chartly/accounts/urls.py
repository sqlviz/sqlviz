from django.conf.urls import patterns, url
urlpatterns = patterns('',
    (r'^login$', 'django.contrib.auth.views.login', {'template_name': 'templates/faccounts/login.html'}),
    (r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
)