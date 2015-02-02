import json

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from ..factories import DbFactory


class QueryInteractiveAPITest(TransactionTestCase):

    username = "username"
    password = "password"

    def setUp(self):
        self.user = self.create_user()
        self.login()
        self.db = self.mock_database()

    def create_user(self, **defaults):
        kwargs = {
            'username': self.username,
            'password': self.password,
            'email': "u@example.com",
        }
        kwargs.update(defaults)
        return User.objects.create_user(**kwargs)

    def login(self):
        self.client.login(username=self.username, password=self.password)

    def mock_database(self):
        return DbFactory()

    def test_db_data_con(self):
        url = '/app/api/database_explorer/?con_id=%s' % (self.db.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        db_list = ['scratch', 'test', 'test_django']
        for db in db_list:
            self.assertIn([db], data['data']['data'])

    def test_db_data_db(self):
        url = '/app/api/database_explorer/?con_id=%s&db_id=%s' \
            % (self.db.id, self.db.db)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        known_good_tables = ['auth_group', 'website_query', 'django_admin_log']
        for table in known_good_tables:
            self.assertIn([table], data['data']['data'])

    def test_db_data_table(self):
        response = self.client.get(
            '/app/api/database_explorer/?con_id=%s' % (self.db.id) +
            '&db_id=%s&table_id=auth_user' % (self.db.db)
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        row = [['id', 'int(11)', 'NO', 'PRI', None, 'auto_increment']]
        self.assertIn(row, data['data']['data'])

    def test_simple_query_interactive(self):
        query_text = 'select * from auth_user'
        response = self.client.post(
            '/app/api/query_interactive/',
            {'query_text': query_text, 'db': self.db.id},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        user_data = data['data']['data'][0]

        self.assertLess(data['time_elapsed'], 2)
        self.assertIn(self.username, user_data)
        self.assertIn(self.user.email, user_data)
        self.assertIn(self.user.id, user_data)
