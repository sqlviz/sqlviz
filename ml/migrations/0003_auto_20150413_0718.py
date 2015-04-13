# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0002_model_blob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model_blob',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
    ]
