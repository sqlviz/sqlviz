import json

from django.contrib.auth.models import User, Group
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


class QueryAPIPermissionTest(TransactionTestCase):

    username = "username"
    password = "password"

    def setUp(self):
        self.user = self.create_user()
        self.login()

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

    def make_query(self, with_tags=True):
        if with_tags:
            kwargs = {
                'tags': ['perm1', 'perm2'],
                'db__tags': ['perm3', 'perm4'],
            }
        else:
            kwargs = {}
        return QueryFactory(owner=self.user, **kwargs)

    def get_query(self, query):
        response = self.client.get('/app/api/query/{}'.format(query.id))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        return data

    def test_without_permissions(self):
        """Test user with no permissions set on query or DB."""
        query = self.make_query(with_tags=False)
        data = self.get_query(query)
        self.assertFalse(data['error'])

    def test_no_shared_permission(self):
        """Test user with no shared permissions to query or DB."""
        query = self.make_query(with_tags=True)
        data = self.get_query(query)
        self.assertTrue(data['error'])
        self.assertIn("permission", data['data'])

    def test_query_permission(self):
        """Test user with query permission."""
        self.user.groups.create(name='perm2')
        query = self.make_query(with_tags=True)
        data = self.get_query(query)
        self.assertFalse(data['error'])

    def test_db_permission(self):
        """Test user with DB permission."""
        self.user.groups.create(name='perm3')
        query = self.make_query(with_tags=True)
        data = self.get_query(query)
        self.assertFalse(data['error'])

    def test_inactive_user(self):
        """Test inactive user with."""
        self.user.is_active = False
        self.user.save()
        query = self.make_query(with_tags=False)
        data = self.get_query(query)
        self.assertTrue(data['error'])
        self.assertIn("Active", data['data'])

    def test_staff_user_with_no_shared_permission(self):
        """Test staff user with no shared permissions to query or DB."""
        self.user.is_staff = True
        self.user.save()
        query = self.make_query(with_tags=True)
        data = self.get_query(query)
        self.assertTrue(data['error'])
        self.assertIn("permission", data['data'])

    def test_superuser_with_no_shared_permission(self):
        """Test superuser with no shared permissions to query or DB."""
        self.user.is_superuser = True
        self.user.save()
        query = self.make_query(with_tags=True)
        data = self.get_query(query)
        self.assertFalse(data['error'])
