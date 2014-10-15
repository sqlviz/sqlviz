from django.conf.urls import patterns, url, include
urlpatterns = patterns('',
    (r'^login$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
    (r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'})
)