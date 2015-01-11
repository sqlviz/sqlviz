from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from encrypted_fields import EncryptedCharField
from django.core.exceptions import ValidationError
from taggit.managers import TaggableManager
from django.conf import settings
from django.db.models.signals import post_save
from dateutil.relativedelta import relativedelta
import re
import time
import json
import datetime

import query

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
    password_encrypted = EncryptedCharField(max_length=1024,) # TODO FIX SPELLING MISTAKE
    create_time = models.DateTimeField(auto_now_add = True, editable = False)
    modified_time = models.DateTimeField(auto_now = True, editable =  False)
    tags = TaggableManager(blank=True)
    def __str__(self):
        return self.name_short

    def clean(self):
        return True # TODO Validate database connection

class Query(models.Model):
    title =  models.CharField(unique = True, max_length = 124, help_text = 'Primary Short Name Used for URL mappings')
    description = models.TextField(max_length = 200)
    description_long = models.TextField(max_length=  1024, blank = True)
    query_text = models.TextField(max_length = 2048, help_text = 'Query to Run')
    insert_limit = models.BooleanField(default = True, help_text = 'Insert limit 1000 to end of query')
    db = models.ForeignKey(Db)
    owner = models.ForeignKey(User)
    hide_index = models.BooleanField(default=False, help_text = 'Hide from Main Search')
    hide_table = models.BooleanField(default=False, help_text = 'Supress Data output in display')
    chart_type = models.CharField(max_length=10,
                                      choices=(('None','None'),('line','line'),('bar','bar'),('column','column'),('area','area'),('country','country')),
                                      default='None')
    pivot_data = models.BooleanField(default=False,  help_text = 'Pivot data around first/second columns.  Nulls filled with 0')
    cumulative = models.BooleanField(default=False,  help_text = 'Run cumulatie sum')
    log_scale_y = models.BooleanField(default=False,  help_text = 'Log scale Y axis')
    stacked = models.BooleanField(default=False, help_text = 'Stack graph Type')
    create_time = models.DateTimeField(auto_now_add = True, editable = False)
    modified_time = models.DateTimeField(auto_now = True, editable =  False)
    graph_extra = models.TextField(blank = True, help_text = 'JSON form of highcharts formatting') # SHOULD INCLUDE default={} in ADMIN!
    image = models.ImageField(upload_to = settings.MEDIA_ROOT + '/thumbnails', max_length = 2048, blank = True)
    cacheable = models.BooleanField(default = True, help_text = 'allows this query result to be cached')
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return "%s: %s" % (self.id, self.title)

    def __str__(self):
        return "%s: %s" % (self.id, self.title)
        
    def get_absolute_url(self):
        return reverse('website.query', args=[str(self.id)])

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

        if self.graph_extra == "" or self.graph_extra is None:
            self.graph_extra = "{}"
        try:
            json.loads(self.graph_extra)
        except:
            raise ValidationError("Graph Extra must be JSON!")
        
        # Validate that query runs!
        """
        try:
            try:
                Q = query.Manipulate_Data(query_text = 'explain ' + self.query_text, db = self.db, user = self.owner)
                Q.run_query()
            except Exception, e:
                # Somethings are un-explainable
                Q = query.Manipulate_Data(query_text = self.query_text, db = self.db, user = self.owner)
                Q.run_query()
        except Exception, e:
            raise ValidationError("Query must run: %s" % (e))"""

class QueryProcessing(models.Model):
    class Meta:
        unique_together = ['query', 'attribute']
    query = models.ForeignKey(Query)
    attribute = models.CharField(max_length=16)
    value = models.CharField(max_length=128)

class QueryDefault(models.Model):
    class Meta:
        unique_together = ['query', 'search_for']
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

class QueryPrecedent(models.Model):
    final_query = models.ForeignKey(Query)
    preceding_query = models.ForeignKey(Query, related_name = "+")

    def clean(self):
        def cycle_check(self):
            # Check to ensure no cycles
            pass
        return True

class Dashboard(models.Model):
    title =  models.CharField(unique = True, max_length = 124, help_text = 'Primary Short Name Used for URL mappings')
    description = models.TextField(max_length=  200)
    description_long = models.TextField(max_length=  1024)
    owner = models.ForeignKey(User)
    hide_index = models.BooleanField(default=False, help_text = 'Hide from Main Search')
    create_time = models.DateTimeField(auto_now_add = True, editable = False)
    modified_time = models.DateTimeField(auto_now = True, editable =  False)
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return "%s: %s" % (self.id, self.title)

    def __str__(self):
        return "%s: %s" % (self.id, self.title)

class DashboardQuery(models.Model):
    class Meta:
        unique_together = ['query', 'dashboard']
    query = models.ForeignKey(Query)
    dashboard = models.ForeignKey(Dashboard)
    order = models.IntegerField(default = 1)

    def __str__(self):
        return "%s : %s" % (self.query, self.dashboard)

    def __unicode__(self):
        return "%s : %s" % (self.query, self.dashboard)

class QueryCache(models.Model):
    query = models.ForeignKey(Query)
    table_name = models.CharField(unique=True, max_length=128)
    run_time = models.DateTimeField(auto_now_add = True, editable = False)
    hash = models.CharField(max_length=1024)

    def __str__(self):
        return "%s : %s" % (self.query, self.table_name)

    def expired(self):
        if self.run_time + relativedelta(days = 1) < datetime.date.today():
            return True
        else:
            return False

class QueryView(models.Model):
    user = models.ForeignKey(User)
    query = models.ForeignKey(Query)
    view_time = models.DateTimeField(auto_now_add = True, editable = False)
    def __str__(self):
        return "%s : %s : %s" % (self.user, self.query, self.view_time)

## POST SAVE TO CREATE IMAGE FOR QUERY  
def post_save_handler_query(sender, instance, **kwargs):
    post_save.disconnect(post_save_handler_query, sender=Query)
    if instance.chart_type not in ['None','country']:
        LQ = query.Load_Query(query_id = instance.id, user = instance.owner)
        Q = LQ.prepare_query()
        Q.run_query()
        Q.run_manipulations()
        image = Q.generate_image()
        instance.image = image
        instance.save()
    post_save.connect(post_save_handler_query, sender=Query)
post_save.connect(post_save_handler_query, sender=Query)