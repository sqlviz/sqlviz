# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DimDjia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('price', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DimGdpData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=128)),
                ('continent', models.CharField(max_length=128)),
                ('country', models.CharField(max_length=128)),
                ('gdp', models.IntegerField()),
                ('population', models.IntegerField()),
                ('region', models.CharField(max_length=128)),
                ('users', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
