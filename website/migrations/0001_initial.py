# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import encrypted_fields.fields
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'Primary Short Name Used for URL mappings', unique=True, max_length=124)),
                ('description', models.TextField(max_length=200)),
                ('description_long', models.TextField(max_length=1024)),
                ('hide_index', models.BooleanField(default=False, help_text=b'Hide from Main Search')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DashboardQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=1)),
                ('dashboard', models.ForeignKey(to='website.Dashboard')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Db',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_short', models.CharField(unique=True, max_length=10)),
                ('name_long', models.CharField(unique=True, max_length=128)),
                ('type', models.CharField(default=b'None', max_length=10, choices=[(b'MySQL', b'MySQL'), (b'Postgres', b'Postgres'), (b'Hive2', b'Hive2')])),
                ('host', models.CharField(max_length=1024)),
                ('db', models.CharField(max_length=1024)),
                ('port', models.IntegerField()),
                ('username', models.CharField(max_length=128)),
                ('password_encrypted', encrypted_fields.fields.EncryptedCharField(max_length=1024)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'Primary Short Name Used for URL mappings', unique=True, max_length=124)),
                ('description', models.TextField(max_length=200)),
                ('description_long', models.TextField(max_length=1024, blank=True)),
                ('query_text', models.TextField(help_text=b'Query to Run', max_length=2048)),
                ('insert_limit', models.BooleanField(default=True, help_text=b'Insert limit 1000 to end of query')),
                ('hide_index', models.BooleanField(default=False, help_text=b'Hide from Main Search')),
                ('hide_table', models.BooleanField(default=False, help_text=b'Supress Data output in display')),
                ('chart_type', models.CharField(default=b'None', max_length=10, choices=[(b'None', b'None'), (b'line', b'line'), (b'bar', b'bar'), (b'column', b'column'), (b'area', b'area'), (b'country', b'country')])),
                ('pivot_data', models.BooleanField(default=False, help_text=b'Pivot data around first/second columns.  Nulls filled with 0')),
                ('cumulative', models.BooleanField(default=False, help_text=b'Run cumulatie sum')),
                ('log_scale_y', models.BooleanField(default=False, help_text=b'Log scale Y axis')),
                ('stacked', models.BooleanField(default=False, help_text=b'Stack graph Type')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('graph_extra', models.TextField(help_text=b'JSON form of highcharts formatting', blank=True)),
                ('image', models.ImageField(max_length=2048, upload_to=b'/home/trey/repos/business/chartly/media//thumbnails', blank=True)),
                ('db', models.ForeignKey(to='website.Db')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QueryCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('table_name', models.CharField(unique=True, max_length=128)),
                ('run_time', models.DateTimeField(auto_now_add=True)),
                ('query', models.ForeignKey(to='website.Query')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QueryDefault',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('search_for', models.CharField(max_length=128)),
                ('replace_with', models.CharField(help_text=b'For todays date set replace with = today and data_type = Date', max_length=1024)),
                ('data_type', models.CharField(default=b'String', max_length=10, choices=[(b'Numeric', b'Numeric'), (b'String', b'String'), (b'Date', b'Date')])),
                ('query', models.ForeignKey(to='website.Query')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QueryPrecedent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('final_query', models.ForeignKey(to='website.Query')),
                ('preceding_query', models.ForeignKey(related_name='+', to='website.Query')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QueryProcessing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attribute', models.CharField(max_length=16)),
                ('value', models.CharField(max_length=128)),
                ('query', models.ForeignKey(to='website.Query')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QueryView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('view_time', models.DateTimeField(auto_now_add=True)),
                ('query', models.ForeignKey(to='website.Query')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='queryprocessing',
            unique_together=set([('query', 'attribute')]),
        ),
        migrations.AlterUniqueTogether(
            name='querydefault',
            unique_together=set([('query', 'search_for')]),
        ),
        migrations.AddField(
            model_name='dashboardquery',
            name='query',
            field=models.ForeignKey(to='website.Query'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='dashboardquery',
            unique_together=set([('query', 'dashboard')]),
        ),
    ]
