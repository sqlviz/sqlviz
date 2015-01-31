from django.contrib import admin
import models


class EmailUserAdmin(admin.TabularInline):
    model = models.EmailUser
    extra = 3


class JobAdmin(admin.ModelAdmin):
    model = models.Job
    inlines = [EmailUserAdmin]

admin.site.register(models.Job, JobAdmin)
