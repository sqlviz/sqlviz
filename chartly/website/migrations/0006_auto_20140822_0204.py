# encoding: utf8
from django.db import models, migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20140822_0200'),
    ]

    operations = [
        migrations.AddField(
            model_name='db',
            name='host',
            field=models.CharField(default='asdfqwer', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='db',
            name='password_encrpyed',
            field=encrypted_fields.fields.EncryptedCharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='db',
            name='name_long',
            field=models.CharField(unique=True, max_length=128),
        ),
    ]
