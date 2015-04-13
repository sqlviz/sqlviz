# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20150118_2210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='image',
            field=models.ImageField(max_length=2048, upload_to=b'/Users/matthewfeldman/Documents/sqlviz_git/media//thumbnails', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='query',
            name='pivot_data',
            field=models.BooleanField(default=False, help_text=b'Pivot data around 1rst&2nd columns. Nulls filled with 0'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='querydefault',
            name='replace_with',
            field=models.CharField(help_text=b'For todayreplace with = today and data_type = Date', max_length=1024),
            preserve_default=True,
        ),
    ]
