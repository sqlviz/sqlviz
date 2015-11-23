# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('table_explorer', '0002_auto_20151005_0201'),
    ]

    operations = [
        migrations.CreateModel(
            name='Column',
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
                ('table', models.ForeignKey(to='table_explorer.Table')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='columnn',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='columnn',
            name='table',
        ),
        migrations.DeleteModel(
            name='Columnn',
        ),
        migrations.AlterUniqueTogether(
            name='column',
            unique_together=set([('table', 'name')]),
        ),
    ]
