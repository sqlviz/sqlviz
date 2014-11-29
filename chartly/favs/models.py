from django.db import models
import website.models
from django.contrib.auth.models import User

class FavoriteDashboard(models.Model):
    class Meta:
        unique_together = ['user', 'dashboard']
    user = models.ForeignKey(User)
    dashboard = models.ForeignKey('website.Dashboard')

    def __str__(self):
        return '%s %s' (self.user, self.dashboard)

class FavoriteQuery(models.Model):
    class Meta:
        unique_together = ['user', 'query']
    user = models.ForeignKey(User)
    query = models.ForeignKey('website.Query')

    def __str__(self):
        return '%s %s' (self.user, self.query)
