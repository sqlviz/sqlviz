# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_auto_20140825_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='hide_index',
            field=models.BooleanField(default=False, help_text='Hide from Main Search'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='query',
            name='chart_type',
            field=models.CharField(default='None', max_length=10, choices=[('None', 'None'), ('line', 'line'), ('bar', 'bar'), ('column', 'column'), ('area', 'area')]),
        ),
    ]
