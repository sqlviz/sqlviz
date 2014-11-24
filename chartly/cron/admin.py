from django.contrib import admin

# Register your models here.
#import cron.models
from models import *


class EmailUserAdmin(admin.TabularInline):
    model = EmailUser    
    extra = 3

class SchedueleAdmin(admin.ModelAdmin):
    model = Scheduele
    inlines = [EmailUserAdmin]

admin.site.register(Scheduele, SchedueleAdmin)
#admin.site.register(EmailUser, EmailUserAdmin)