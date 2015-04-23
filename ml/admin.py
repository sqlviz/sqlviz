from django.contrib import admin
from models import machine_learning_model


class MlAdmin(admin.ModelAdmin):
    model = machine_learning_model

admin.site.register(machine_learning_model, MlAdmin)
