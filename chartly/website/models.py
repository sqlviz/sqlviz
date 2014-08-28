import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from encrypted_fields import EncryptedCharField
from django.core.exceptions import ValidationError
import re
import time
#import MySQLdb

class Db(models.Model):
    name_short = models.CharField(unique=True,max_length=10)
    name_long = models.CharField(unique=True,max_length=128)
    type = models.CharField(max_length=10,
                                  choices=(('MySQL','MySQL'),('Postgres','Postgres'),('Hive2','Hive2')),
                                  default='None')
    host = models.CharField(max_length=1024)
    db = models.CharField(max_length=1024)
    port = models.IntegerField()
    username = models.CharField(max_length=128)
    password_encrpyed = EncryptedCharField(max_length=1024)
    def __str__(self):
        return self.name_short

class Query(models.Model):
    title =  models.CharField(unique = True, max_length = 124, help_text = 'Primary Short Name Used for URL mappings')
    description = models.TextField(max_length = 200)
    description_long = models.TextField(max_length=  1024)
    query_text = models.TextField(max_length = 2048, help_text = 'Query to Run')
    insert_limit = models.BooleanField(default = True, help_text = 'Insert limit 1000 to end of query')
    database = models.ForeignKey(Db)
    owner = models.ForeignKey(User)
    hide_index = models.BooleanField(default=False, help_text = 'Hide from Main Search')
    hide_table = models.BooleanField(default=False, help_text = 'Supress Data output in display')
    pivot_data = models.BooleanField(default=False,  help_text = 'Pivot data around first/second columns.  Nulls filled with 0')
    chart_type = models.CharField(max_length=10,
                                      choices=(('None','None'),('line','line'),('bar','bar'),('column','column'),('area','area')),
                                      default='None')
    stacked = models.BooleanField(default=False, help_text = 'Stack graph Type')
    create_time = models.DateTimeField(auto_now_add = True, editable = False)
    modified_time = models.DateTimeField(auto_now = True, editable =  False)

    def __str__(self):
        return self.title
    def clean(self):
        # dont allow queries to contain blacklist words
        blacklist = ['delete','insert','update','alter','drop']
        def findWholeWord(w):
            return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
        for word in blacklist:
            if findWholeWord(word)(self.query_text) != None:
                raise ValidationError('Queries can not contain %s' % word)
        if self.chart_type == 'None' and self.stacked == 1:
            raise ValidationError("Can't stack an invisible chart")

class QueryChart(models.Model):
    query = models.ForeignKey(Query)

class QueryDefault(models.Model):
    query = models.ForeignKey(Query)
    search_for = models.CharField(max_length=128)
    replace_with = models.CharField(max_length=1024, help_text ='For todays date set replace with = today and data_type = Date')
    data_type = models.CharField(max_length=10,
                                  choices=(('Numeric','Numeric'),('String','String'),('Date','Date')),
                                  default='String')
    def __str__(self):
        return "%s : %s " % (self.query, self.search_for[0:10])

    def replace_with_cleaned(self):
        if self.data_type == "Date" and self.replace_with.lower() == 'today':
            return time.strftime("%Y-%m-%d") 
        else:
            return self.replace_with

    def clean(self):
        def valid_date(datestring):
            pass
            ## TODO CHECK
        return True

class Dashboard(models.Model):
    title =  models.CharField(unique = True, max_length = 124, help_text = 'Primary Short Name Used for URL mappings')
    description = models.TextField(max_length=  200)
    description_long = models.TextField(max_length=  1024)
    owner = models.ForeignKey(User)
    hide_index = models.BooleanField(default=False, help_text = 'Hide from Main Search')
    create_time = models.DateField(auto_now_add = True, editable = False)
    modified_time = models.DateField(auto_now = True, editable =  False)

    def __str__(self):
        return self.title

class DashboardQuery(models.Model):
    query = models.ForeignKey(Query)
    dashboard = models.ForeignKey(Dashboard)
    order = models.IntegerField()

    def __str__(self):
        return "%s : %s" % (self.query, self.dashboard)

class QueryFavorite(models.Model):
    user = models.ForeignKey(User)
    query = models.ForeignKey(Query)

    def __str__(self):
        return "%s : %s" % (self.user, self.query)

class DashboardFavorite(models.Model):
    user = models.ForeignKey(User)
    dashboard = models.ForeignKey(Dashboard)    
    def __str__(self):
        return "%s : %s" % (self.user, self.dashboard)
class QueryView(models.Model):
    user = models.ForeignKey(User)
    query = models.ForeignKey(Query)
    view_time = models.DateTimeField(auto_now_add = True, editable = False)
    def __str__(self):
        return "%s : %s : %s" % (self.user, self.query, self.view_time)