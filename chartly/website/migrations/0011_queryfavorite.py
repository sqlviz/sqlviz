# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0010_dashboardquery'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryFavorite',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field=u'id')),
                ('query', models.ForeignKey(to='website.Query', to_field=u'id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
