import json

from django.contrib.auth.models import User
from django.test import TransactionTestCase

from ..factories import QueryFactory


class QueryAPITest(TransactionTestCase):

    username = "username"
    password = "password"

    def create_user(self):
        return User.objects.create_superuser(
            username=self.username,
            password=self.password,
            email="u@example.com",
        )

    def login(self):
        self.client.login(username=self.username, password=self.password)

    def test_not_logged_in(self):
        response = self.client.get('/app/api/query/1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['location'],
            "http://testserver/accounts/login?next=/app/api/query/1",
        )

    def test_invalid_query_id(self):
        self.create_user()
        self.login()
        response = self.client.get('/app/api/query/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {
            'time_elapsed': 0,
            'data': "list index out of range",
            'error': True,
        })

    def test_valid_query(self):
        user = self.create_user()
        self.login()
        query = QueryFactory(
            query_text="""
                select
                    id, username
                from
                    auth_user
            """,
            owner=user,
        )
        response = self.client.get('/app/api/query/{}'.format(query.id))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertLess(data['time_elapsed'], 1)
        del data['time_elapsed']
        self.assertEqual(data, {
            'error': False,
            'data': {
                'columns': ['id', 'username'],
                'data': [[user.id, user.username]],
            },
        })
