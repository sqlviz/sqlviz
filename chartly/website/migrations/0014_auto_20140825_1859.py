# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_auto_20140822_0618'),
    ]

    operations = [
        migrations.RenameField(
            model_name='db',
            old_name='db_type',
            new_name='type',
        ),
    ]
