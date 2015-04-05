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
            field=models.ImageField(max_length=2048, upload_to=b'/Users/matthewfeldman/Documents/sqlviz/media//thumbnails', blank=True),
            preserve_default=True,
        ),
    ]
