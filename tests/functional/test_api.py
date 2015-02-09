import json

from ..factories import QueryFactory, QueryDefaultFactory, UserFactory
from .testcases import APITestCase


def create_users(user_count=100):
    first_names = ['John', 'Bob', 'Dilbert']
    last_names = ['Smith', 'Brown', 'Yu', 'Green']
    return [
        UserFactory(
            first_name=first_names[i % len(first_names)],
            last_name=last_names[i % len(last_names)]
        )
        for i in range(user_count)
    ]


class QueryAPITestCase(APITestCase):

    def get_query(self, query_id, query_params=None):
        url = '/api/query/{}'.format(query_id)
        if query_params:
            query_string = "&".join("=".join(i) for i in query_params.items())
            url = "{}?{}".format(url, query_string)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)

    def assertQueryData(self, query_data, **kwargs):
        kwargs.setdefault('cached', False)
        kwargs.setdefault('error', False)
        self.assertLess(query_data['time_elapsed'], 1)
        query_data.pop('time_elapsed')
        self.assertEqual(query_data, kwargs)


class QueryAPITest(QueryAPITestCase):

    def test_not_logged_in(self):
        response = self.client.get('/api/query/1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['location'],
            "http://testserver/accounts/login?next=/api/query/1",
        )

    def test_invalid_query_id(self):
        """
        Test a 404 for query api
        """
        self.create_user()
        self.login()
        data = self.get_query(1)
        self.assertQueryData(data, error=True,
                             data="No Query matches the given query.")

    def test_unsafe_query(self):
        user = self.create_user()
        self.login()
        query = QueryFactory(
            query_text="""
                delete
                    *
                from
                    auth_user
                where
                    id < 0
                """,
            owner=user,
        )
        data = self.get_query(query.id)
        self.assertQueryData(data, error=True,
                         data='Query contained delete -- Can not be run')

    def test_valid_query(self):
        user = self.create_user()
        query = QueryFactory(
            query_text="select id, username from auth_user",
            owner=user,
        )
        self.login()
        data = self.get_query(query.id)
        self.assertQueryData(data, data={
            'columns': ['id', 'username'],
            'data': [[user.id, user.username]],
        })

    def test_pivot(self):
        """
        Create test user data set and run pivot on it
        """
        create_users()
        user = self.create_user()
        self.login()
        query = QueryFactory(
            query_text="""
                select
                    first_name, last_name, count(1) user_count
                from
                    auth_user
                where
                    first_name != '' and last_name != ''
                group by
                    1,2
            """,
            owner=user,
            pivot_data=True
        )
        data = self.get_query(query.id)
        self.assertQueryData(data, data={
            'columns': ['first_name', 'Brown', 'Green', 'Smith', 'Yu'],
            'data': [
                [u'Bob', 9.0, 8.0, 8.0, 8.0],
                [u'Dilbert', 8.0, 8.0, 8.0, 9.0],
                [u'John', 8.0, 9.0, 9.0, 8.0]
            ],
        })


class QueryParameterTest(QueryAPITestCase):
    def mock_valid_user_and_parameter_query(self):
        create_users()
        user = self.create_user()
        self.login()
        query = QueryFactory(
            query_text="""
                select
                    first_name
                from
                    auth_user
                where
                    date_joined > "<DATE>"
                    and first_name = "<NAME>"
                limit
                    1
            """,
            owner=user,
        )
        defaults = []
        defaults.append(QueryDefaultFactory(
            query=query,
            search_for="<DATE>",
            replace_with="2014-04-01",
            data_type="Date",
        ))
        defaults.append(QueryDefaultFactory(
            query=query,
            search_for="<NAME>",
            replace_with="John",
            data_type="String",
        ))
        return (user, query, defaults)

    def test_parameters_default(self):
        (user, query, defaults) = self.mock_valid_user_and_parameter_query()
        data = self.get_query(query.id)
        self.assertQueryData(data, data={
            'columns': ['first_name'],
            'data': [['John']],
        })

    def test_parameters_request(self):
        (user, query, defaults) = self.mock_valid_user_and_parameter_query()
        name = 'Bob'
        data = self.get_query(query.id, {'<NAME>': name})
        self.assertQueryData(data, data={
            'columns': ['first_name'],
            'data': [[name]],
        })


class QueryCacheTest(QueryAPITestCase):

    def test_used_cache(self):
        """
        Runs query twice to see if caching goes from False to True
        """
        user = self.create_user()
        query = QueryFactory(
            query_text="select id, username from auth_user",
            owner=user,
        )
        self.login()
        data = self.get_query(query.id)
        # TODO make this run a longer query and validate the cache is faster
        self.assertQueryData(data, data={
            'columns': ['id', 'username'],
            'data': [[user.id, user.username]],
        })
        data = self.get_query(query.id)
        self.assertQueryData(data, cached=True, data={
            'columns': ['id', 'username'],
            'data': [[user.id, user.username]],
        })
        return (user, query)

    def test_no_cache_request(self):
        # Run Suite from before
        (user, query) = self.test_used_cache()
        # Now run with caching turned off
        # TODO use a url parameter in get here
        data = self.get_query(query.id, {'cacheable': "False"})
        self.assertQueryData(data, data={
            'columns': ['id', 'username'],
            'data': [[user.id, user.username]],
        })


class QueryAPIPermissionTest(QueryAPITestCase):

    def setUp(self):
        self.user = self.create_user()
        self.login()

    def make_query(self, with_tags=True):
        if with_tags:
            kwargs = {
                'tags': ['perm1', 'perm2'],
                'db__tags': ['perm3', 'perm4'],
            }
        else:
            kwargs = {}
        return QueryFactory(owner=self.user, **kwargs)

    def test_without_permissions(self):
        """Test user with no permissions set on query or DB."""
        query = self.make_query(with_tags=False)
        data = self.get_query(query.id)
        self.assertFalse(data['error'])

    def test_no_shared_permission(self):
        """Test user with no shared permissions to query or DB."""
        query = self.make_query(with_tags=True)
        data = self.get_query(query.id)
        self.assertTrue(data['error'])
        self.assertIn("permission", data['data'])

    def test_query_permission(self):
        """Test user with query permission."""
        self.user.groups.create(name='perm2')
        query = self.make_query(with_tags=True)
        data = self.get_query(query.id)
        self.assertFalse(data['error'])

    def test_db_permission(self):
        """Test user with DB permission."""
        self.user.groups.create(name='perm3')
        query = self.make_query(with_tags=True)
        data = self.get_query(query.id)
        self.assertFalse(data['error'])

    def test_inactive_user(self):
        """Test inactive user with."""
        self.user.is_active = False
        self.user.save()
        query = self.make_query(with_tags=False)
        data = self.get_query(query.id)
        self.assertTrue(data['error'])
        self.assertIn("Active", data['data'])

    def test_staff_user_with_no_shared_permission(self):
        """Test staff user with no shared permissions to query or DB."""
        self.user.is_staff = True
        self.user.save()
        query = self.make_query(with_tags=True)
        data = self.get_query(query.id)
        self.assertTrue(data['error'])
        self.assertIn("permission", data['data'])

    def test_superuser_with_no_shared_permission(self):
        """Test superuser with no shared permissions to query or DB."""
        self.user.is_superuser = True
        self.user.save()
        query = self.make_query(with_tags=True)
        data = self.get_query(query.id)
        self.assertFalse(data['error'])
