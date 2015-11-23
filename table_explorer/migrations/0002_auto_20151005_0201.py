# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('table_explorer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='database_name',
            field=models.CharField(default='test', max_length=124),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='table',
            unique_together=set([('db', 'database_name', 'title')]),
        ),
    ]
