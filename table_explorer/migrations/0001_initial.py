# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20151005_0143'),
    ]

    operations = [
        migrations.CreateModel(
            name='Columnn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=124)),
                ('type', models.CharField(max_length=124)),
                ('min', models.CharField(max_length=124)),
                ('max', models.CharField(max_length=124)),
                ('mode', models.CharField(max_length=124)),
                ('mean', models.FloatField()),
                ('histogram_json', models.TextField(max_length=1000)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=124)),
                ('description', models.TextField(max_length=200)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('db', models.ForeignKey(to='website.Db')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='columnn',
            name='table',
            field=models.ForeignKey(to='table_explorer.Table'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='columnn',
            unique_together=set([('table', 'name')]),
        ),
    ]
