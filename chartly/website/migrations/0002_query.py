# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Primary Short Name Used for URL mappings', unique=True, max_length=124)),
                ('description', models.TextField(max_length=200)),
                ('description_long', models.TextField(max_length=1024)),
                ('query_text', models.TextField(help_text='Query to Run', max_length=2048)),
                ('insert_limit', models.BooleanField(default=True, help_text='Insert limit 1000 to end of query')),
                ('database', models.ForeignKey(to='website.Db', to_field=u'id')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field=u'id')),
                ('hide_index', models.BooleanField(default=False, help_text='Hide from Main Search')),
                ('hide_table', models.BooleanField(default=False, help_text='Supress Data output in display')),
                ('pivot_data', models.BooleanField(default=False, help_text='Pivot data around first/second columns.  Nulls filled with 0')),
                ('chart_type', models.CharField(default='None', max_length=10, choices=[('None', 'None'), ('Line', 'Line'), ('Bar', 'Bar'), ('Column', 'Column'), ('Area', 'Area')])),
                ('stacked', models.BooleanField(default=False, help_text='Stack graph Type')),
                ('create_time', models.DateField(auto_now_add=True)),
                ('modified_time', models.DateField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
