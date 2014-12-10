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

class QueryProcessingAdmin(admin.TabularInline):
    model = QueryProcessing

class QueryAdminForm(forms.ModelForm):
    class Meta:
        model = Query
        widgets = {'query_text' : AceWidget(mode='sql')}
        exclude = ()

class QueryAdmin(admin.ModelAdmin):
    form = QueryAdminForm
    inlines = [QueryDefaultAdmin, QueryPrecedentAdmin, QueryProcessingAdmin]
    list_display = ('id', 'title', 'db','owner','chart_type','modified_time')
    save_as = True

class DbAdminForm(forms.ModelForm):
    class Meta:
        model = Db
        widgets = {'password_encrypted' : PasswordInput()}
        exclude = ()

class DbAdmin(admin.ModelAdmin):
    form = DbAdminForm
    list_display = ('id', 'name_short', 'type','port','username')

class DashboardQueryAdmin(admin.TabularInline):
    model = DashboardQuery
    def get_form(self, request, obj=None, **kwargs):
        form = super(DashboardQueryAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['order'].initial = 1
        return form


class DashboardAdmin(admin.ModelAdmin):
    model = Dashboard
    inlines = [DashboardQueryAdmin]
    list_display = ('id', 'title', 'owner','modified_time')


admin.site.register(Query, QueryAdmin)
admin.site.register(Db, DbAdmin)
admin.site.register(Dashboard, DashboardAdmin)