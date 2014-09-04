# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_auto_20140826_0014'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryPrecedent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('final_query', models.ForeignKey(to='website.Query')),
                ('preceding_query', models.ForeignKey(related_name=b'+', to='website.Query')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='query',
            name='log_scale_y',
            field=models.BooleanField(default=False, help_text=b'Log scale Y axis'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='querydefault',
            name=b'replace_with',
            field=models.CharField(help_text=b'For todays date set replace with = today and data_type = Date', max_length=1024),
        ),
    ]
