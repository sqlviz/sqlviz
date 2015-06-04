from django.contrib.auth.signals import user_logged_out
from django.contrib import messages
from django.dispatch import receiver
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^login$', 'django.contrib.auth.views.login', {
        'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout', {
        'next_page': 'accounts:login'}, name='logout'),
)

@receiver(user_logged_out)
def user_logout_handler(sender, request, **kwargs):
    messages.info(request, "You have logged out.")
