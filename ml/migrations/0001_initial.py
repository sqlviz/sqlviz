# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20150411_2157'),
    ]

    operations = [
        migrations.CreateModel(
            name='machine_learning_model',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_short', models.CharField(unique=True, max_length=10)),
                ('name_long', models.CharField(unique=True, max_length=128)),
                ('type', models.CharField(default=b'None', max_length=10, choices=[(b'logistic', b'logistic'), (b'linear', b'linear'), (b'tree', b'tree')])),
                ('target_column', models.CharField(max_length=100)),
                ('query', models.ForeignKey(to='website.Query')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
