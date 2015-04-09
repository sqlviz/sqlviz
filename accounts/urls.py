from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView

urlpatterns = patterns('',
                       url(r'^login$', 'django.contrib.auth.views.login', {
                           'template_name': 'accounts/login.html'}, name='login'),
                       url(r'^logout$', 'django.contrib.auth.views.logout', {
                           'next_page': 'accounts:logout_confirm'}, name='logout'),
                       url(r'^logout_confirm$', TemplateView.as_view(
                           template_name='accounts/logout.html'), name='logout_confirm')
                       )
