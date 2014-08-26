# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_dashboardfavorite'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardQuery',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('query', models.ForeignKey(to='website.Query', to_field=u'id')),
                ('dashboard', models.ForeignKey(to='website.Dashboard', to_field=u'id')),
                ('order', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
