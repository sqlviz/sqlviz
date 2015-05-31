# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20150411_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='queryview',
            name='execution_time',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='queryview',
            name='used_cache',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='querydefault',
            name='replace_with',
            field=models.CharField(help_text=b'For today replace with = today and data_type = Date', max_length=1024),
            preserve_default=True,
        ),
    ]
