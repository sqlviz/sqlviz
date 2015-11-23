from django.db import models
from website.models import Db


# Create your models here.
class Table(models.Model):
    class Meta:
        unique_together = ['db', 'database_name','title']
    db = models.ForeignKey(Db)
    database_name = models.CharField(max_length=124)
    title = models.CharField(max_length=124)
    description = models.TextField(max_length=200)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return  self.database_name + self.title

class Column(models.Model):
    class Meta:
        unique_together = ['table', 'name']
    table = models.ForeignKey(Table)
    name = models.CharField(max_length=124)
    type = models.CharField(max_length=124)
    min = models.CharField(max_length=124)
    max = models.CharField(max_length=124)
    mode = models.CharField(max_length=124)
    mean = models.FloatField()
    histogram_json = models.TextField(max_length=1000)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    modified_time = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name
