from django.contrib.auth.models import User

from ..factories import DbFactory
from .testcases import TestCase


class AdminQueryPageTest(TestCase):

    username = "username"
    password = "password"
    initial_url = "/admin/"

    def setUp(self):
        super(AdminQueryPageTest, self).setUp()
        self.user = self.create_user()
        self.login()

    def create_user(self):
        return User.objects.create_superuser(
            username=self.username,
            password=self.password,
            email="u@example.com",
        )

    def login(self):
        self.browser.fill('username', self.username)
        self.browser.fill('password', self.password)
        self.browser.find_by_value('Log in').click()

    def test_invalid_query_id(self):
        db = DbFactory.create()
        self.browser.find_link_by_href("/admin/website/query/add/").click()
        self.browser.fill_form({
            'title': "GDP",
            'description': "National GDP",
            'query_text': """
                select
                    lower(code) country_code,
                    gdp
                from
                    scratch.country_data
                order by
                    gdp desc""",
            'db': str(db.id),
            'owner': str(self.user.id),
            'chart_type': "country",
            'graph_extra': "{}",
        })
        self.browser.find_by_value("Save").click()
        self.assertIn("added", self.browser.find_by_css('.success').text)
