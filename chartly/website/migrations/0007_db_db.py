# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_auto_20140822_0204'),
    ]

    operations = [
        migrations.AddField(
            model_name='db',
            name='db',
            field=models.CharField(default='', max_length=1024),
            preserve_default=False,
        ),
    ]
