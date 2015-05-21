from django.conf import settings
from django.contrib.auth.models import User
import factory

import website.models
import ml.models  # import Db, Query, QueryDefault
import cron.models  # import Job, EmailUser


class TagsFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True

    @factory.post_generation
    def tags(self, create, extracted):
        if create and extracted:
            self.tags.add(*extracted)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda x: "user{}".format(x))
    email = factory.Sequence(lambda x: "user{}@example.com".format(x))
    password = factory.PostGenerationMethodCall('set_password', "password")


class DbFactory(TagsFactory):
    class Meta:
        model = website.models.Db
        exclude = ('DB',)

    DB = settings.DATABASES['default']
    name_short = "default"
    name_long = "default"
    type = "MySQL"
    host = factory.LazyAttribute(lambda a: a.DB['HOST'])
    db = factory.LazyAttribute(lambda a: a.DB['NAME'])
    port = factory.LazyAttribute(lambda a: a.DB['PORT'] or "3306")
    username = factory.LazyAttribute(lambda a: a.DB['USER'])
    password_encrypted = factory.LazyAttribute(lambda a: a.DB['PASSWORD'])


class QueryFactory(TagsFactory):
    class Meta:
        model = website.models.Query

    title = "title"
    description = "description"
    db = factory.SubFactory(DbFactory)
    owner = factory.SubFactory(UserFactory)
    graph_extra = "{}"
    query_text = "select username, last_login from auth_user"
    pivot_data = False


class MlFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ml.models.machine_learning_model
    query = factory.SubFactory(QueryFactory)
    title = 'title'
    type = 'logistic'
    target_column = 'username'


class DashboardFactory(TagsFactory):
    class Meta:
        model = website.models.Dashboard

    title = 'title'
    description = ''
    description_long = ''
    owner = factory.SubFactory(User)


class DashboardQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = website.models.DashboardQuery
    query = factory.SubFactory(QueryFactory)
    dashboard = factory.SubFactory(DashboardFactory)


class QueryDefaultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = website.models.QueryDefault
    query = factory.SubFactory(QueryFactory)
    search_for = "<DEFAULT>"
    replace_with = ""
    data_type = 'String'


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = cron.models.Job
    owner = factory.SubFactory(UserFactory)
    dashboard = factory.SubFactory(DashboardFactory)
    type = 'daily'


class EmailUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = cron.models.EmailUser
    job = factory.SubFactory(JobFactory)
    user = factory.SubFactory(UserFactory)


class QueryPrecedentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = website.models.QueryPrecedent
    final_query = factory.SubFactory(QueryFactory)
    preceding_query = factory.SubFactory(QueryFactory)
