# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0005_auto_20150420_0526'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='machine_learning_model',
            unique_together=set([('query', 'target_column', 'type')]),
        ),
    ]
