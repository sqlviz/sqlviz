# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_query'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryChart',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('query', models.ForeignKey(to='website.Query', to_field=u'id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
