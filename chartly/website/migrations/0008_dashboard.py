# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0007_db_db'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Primary Short Name Used for URL mappings', unique=True, max_length=124)),
                ('description', models.TextField(max_length=200)),
                ('description_long', models.TextField(max_length=1024)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field=u'id')),
                ('create_time', models.DateField(auto_now_add=True)),
                ('modified_time', models.DateField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
