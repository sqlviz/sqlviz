from django.db import models


class DimDjia(models.Model):
    date = models.DateTimeField()
    price = models.IntegerField()


class DimGdpData(models.Model):
    code = models.CharField(max_length=128)
    continent = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    gdp = models.IntegerField()
    population = models.IntegerField()
    region = models.CharField(max_length=128)
    users = models.IntegerField()
