# encoding: utf8
from django.db import models, migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_querydefault'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db',
            name='password_encrpyed',
            field=encrypted_fields.fields.EncryptedTextField(),
        ),
    ]
