from ..factories import DbFactory
from .testcases import LiveServerTestCase


class AdminQueryPageTest(LiveServerTestCase):

    initial_url = "/admin/"

    def setUp(self):
        super(AdminQueryPageTest, self).setUp()
        self.user = self.create_user()
        self.login()

    def create_user(self, **kwargs):
        return super(LiveServerTestCase, self).create_user(
            is_staff=True, is_superuser=True)

    def test_invalid_query_id(self):
        db = DbFactory()
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
