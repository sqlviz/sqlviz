# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0008_dashboard'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardFavorite',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field=u'id')),
                ('dashboard', models.ForeignKey(to='website.Dashboard', to_field=u'id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
