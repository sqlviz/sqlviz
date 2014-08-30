# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0017_auto_20140829_2350'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='log_scale_y',
            field=models.BooleanField(default=False, help_text='Log scale Y axis'),
            preserve_default=True,
        ),
    ]
