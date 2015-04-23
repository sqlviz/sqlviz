# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='model_blob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('blob', models.TextField()),
                ('model_id', models.ForeignKey(to='ml.machine_learning_model')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
