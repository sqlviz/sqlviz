from django.contrib import admin

# Register your models here.
from models import *


class EmailUserAdmin(admin.TabularInline):
    model = EmailUser
    extra = 3


class JobAdmin(admin.ModelAdmin):
    model = Job
    inlines = [EmailUserAdmin]

admin.site.register(Job, JobAdmin)
# admin.site.register(EmailUser, EmailUserAdmin)
