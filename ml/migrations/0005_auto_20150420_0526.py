# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0004_auto_20150420_0522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine_learning_model',
            name='title',
            field=models.CharField(unique=True, max_length=100),
            preserve_default=True,
        ),
    ]
