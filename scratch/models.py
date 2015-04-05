from django.db import models


class DimDjia(models.Model):
    date = models.DateTimeField()
    price = models.IntegerField()
