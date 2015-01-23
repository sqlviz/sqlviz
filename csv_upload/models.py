from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

import pandas as pd
import MySQLdb
# Create your models here.
class csv(models.Model):
    name = models.CharField(max_length=20)
    table_name = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add = True, editable = False)
    file_name = models.FileField(upload_to = settings.MEDIA_ROOT + '/csv', max_length = 2048, blank = True)

    def __str__(self):
        return self.name

    def clean(self):
        return True # TODO Validate database connection

## POST SAVE TO CREATE IMAGE FOR QUERY
def csv_to_sql(sender, instance, **kwargs):
    df = pd.io.parsers.read_csv(instance.file_name, header =0, infer_datetime_format = True)
    db = settings.CUSTOM_DATABASES['write_to']
    con = MySQLdb.connect(host = db['HOST'], port = db['PORT'],
                user = db['USER'], passwd = db['PASSWORD'], db = db['NAME'])
    df.to_sql(instance.table_name, con, flavor='mysql', if_exists='replace', index= False)
    con.close()

post_save.connect(csv_to_sql, sender=csv)
