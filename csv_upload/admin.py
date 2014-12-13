from django.contrib import admin

# Register your models here.
#import cron.models
from models import *



class CSVAdmin(admin.ModelAdmin):
    model = csv

admin.site.register(csv, CSVAdmin)
#admin.site.register(EmailUser, EmailUserAdmin)