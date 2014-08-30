# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0016_auto_20140828_1634'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryPrecedent',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('final_query', models.ForeignKey(to='website.Query', to_field=u'id')),
                ('preceding_query', models.ForeignKey(to='website.Query', to_field=u'id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='DataUpload',
        ),
    ]
