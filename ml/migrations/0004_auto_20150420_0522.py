# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0003_auto_20150413_0718'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine_learning_model',
            name='name_long',
        ),
        migrations.RemoveField(
            model_name='machine_learning_model',
            name='name_short',
        ),
        migrations.AddField(
            model_name='machine_learning_model',
            name='title',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
