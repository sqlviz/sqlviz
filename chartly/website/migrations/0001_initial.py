# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Db',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_short', models.CharField(unique=True, max_length=10)),
                ('db_type', models.CharField(default='None', max_length=10, choices=[('MySQL', 'MySQL'), ('Postgres', 'Postgres'), ('Hive2', 'Hive2')])),
                ('name_long', models.CharField(max_length=1024)),
                ('port', models.IntegerField()),
                ('username', models.CharField(max_length=128)),
                ('password_encrpyed', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
