import json

from .testcases import APITestCase
from ..factories import DbFactory
from django.core.urlresolvers import reverse


class QueryInteractiveAPITest(APITestCase):

    def setUp(self):
        self.user = self.create_user(is_staff=True)
        self.login()
        self.db = DbFactory()

    def get_query(self, params):
        params.setdefault('con_id', self.db.id)
        query_string = "&".join("{}={}".format(*i) for i in params.items())
        url = '/api/database_explorer/?{}'.format(query_string)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)

    def test_db_data_con(self):
        db_list = []  # TODO find something approps for this check
        data = self.get_query({})
        for db in db_list:
            self.assertIn([db], data['data']['data'])
        self.assertGreater(len(data['data']['data']), 3)

    def test_db_data_db(self):
        data = self.get_query({'db_id': self.db.db})
        known_good_tables = ['auth_group', 'website_query', 'django_admin_log']
        for table in known_good_tables:
            self.assertIn([table], data['data']['data'])

    def test_db_data_table(self):
        data = self.get_query({'db_id': self.db.db, 'table_id': "auth_user"})
        row = ['id', 'int(11)', 'NO', 'PRI', None, 'auto_increment']
        self.assertIn(row, data['data']['data'])

    def test_simple_query_interactive(self):
        query_text = 'select * from auth_user'
        response = self.client.post(
            reverse('website:query_interactive_api'),
            {'query_text': query_text, 'db': self.db.id},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        user_data = data['data']['data'][0]

        self.assertLess(data['time_elapsed'], 2)
        self.assertIn(self.username, user_data)
        self.assertIn(self.user.email, user_data)
        self.assertIn(self.user.id, user_data)
