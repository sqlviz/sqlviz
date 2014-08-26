# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_querychart'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryDefault',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('query', models.ForeignKey(to='website.Query', to_field=u'id')),
                ('search_for', models.CharField(max_length=128)),
                ('replace_with', models.CharField(max_length=1024)),
                ('data_type', models.CharField(default='String', max_length=10, choices=[('Numeric', 'Numeric'), ('String', 'String'), ('Date', 'Date')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
