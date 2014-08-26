# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0012_queryview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='modified_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='query',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='queryview',
            name='view_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
