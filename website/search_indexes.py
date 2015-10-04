import datetime
from haystack import indexes
from models import Query, Dashboard


class QueryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    modified_time = indexes.DateTimeField(model_attr='modified_time')

    def get_model(self):
        return Query

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            modified_time__lte=datetime.datetime.now()
        )


class DashboardIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    modified_time = indexes.DateTimeField(model_attr='modified_time')

    def get_model(self):
        return Dashboard

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            modified_time__lte=datetime.datetime.now()
        )
