from django.conf import settings
import factory

from website.models import Db


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
