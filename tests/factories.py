from django.conf import settings
from django.contrib.auth.models import User
import factory

from website.models import Db, Query


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda x: "user{}".format(x))
    email = factory.Sequence(lambda x: "user{}@example.com".format(x))
    password = factory.PostGenerationMethodCall('set_password', "password")


class DbFactory(factory.DjangoModelFactory):
    class Meta:
        model = Db
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


class QueryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Query

    title = "title"
    description = "description"
    db = factory.SubFactory(DbFactory)
    owner = factory.SubFactory(UserFactory)
    graph_extra = "{}"
