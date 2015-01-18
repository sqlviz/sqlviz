# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='cacheable',
            field=models.BooleanField(default=True, help_text=b'allows this query result to be cached'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='querycache',
            name='hash',
            field=models.CharField(default='', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='querycache',
            name='run_time',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
    ]
