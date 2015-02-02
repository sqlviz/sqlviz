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
        correct_response = {u'data': {u'data': [[u'information_schema'], [u'django'], [u'scratch'], [u'test'], [u'test_django']], u'columns': [u'Database']}, u'error': False}
        self.assertEqual(data, correct_response)

    def test_db_data_db(self):
        url = '/app/api/database_explorer/?con_id=%s&db_id=%s' % (self.db.id, self.db.db)
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
        correct_response  = [[u'id', u'int(11)', u'NO', u'PRI', None, u'auto_increment']]
        # , [u'password', u'varchar(128)', u'NO', u'', None, u''], [u'last_login', u'datetime', u'NO', u'', None, u''], [u'is_superuser', u'tinyint(1)', u'NO', u'', None, u''], [u'username', u'varchar(30)', u'NO', u'UNI', None, u''], [u'first_name', u'varchar(30)', u'NO', u'', None, u''], [u'last_name', u'varchar(30)', u'NO', u'', None, u''], [u'email', u'varchar(75)', u'NO', u'', None, u''], [u'is_staff', u'tinyint(1)', u'NO', u'', None, u''], [u'is_active', u'tinyint(1)', u'NO', u'', None, u''], [u'date_joined', u'datetime', u'NO', u'', None, u'']]
        for row in correct_response:
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

