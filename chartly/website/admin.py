from django.contrib import admin
from django import forms
from django.forms import PasswordInput
from django_ace import AceWidget
from models import *

class QueryDefaultAdmin(admin.TabularInline):
    model = QueryDefault

class QueryPrecedentAdmin(admin.TabularInline):
    model = QueryPrecedent    
    fk_name = "final_query"


class QueryAdminForm(forms.ModelForm):
    class Meta:
        model = Query
        widgets = {'query_text' : AceWidget(mode='sql')}
        exclude = ()

class QueryAdmin(admin.ModelAdmin):
    form = QueryAdminForm
    inlines = [QueryDefaultAdmin, QueryPrecedentAdmin]

class DbAdminForm(forms.ModelForm):
    class Meta:
        model = Db
        widgets = {'password_encrpyed' : PasswordInput()}
        exclude = ()

class DbAdmin(admin.ModelAdmin):
    form = DbAdminForm

class DashboardQueryAdmin(admin.TabularInline):
    model = DashboardQuery

class DashboardAdmin(admin.ModelAdmin):
    model = Dashboard
    inlines = [DashboardQueryAdmin]


admin.site.register(Query, QueryAdmin)
admin.site.register(Db, DbAdmin)
admin.site.register(Dashboard, DashboardAdmin)