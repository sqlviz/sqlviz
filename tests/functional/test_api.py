import json

from ..factories import QueryFactory, QueryDefaultFactory, UserFactory, \
    QueryPrecedentFactory
from .testcases import APITestCase
import datetime


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

    def assert_query_data(self, query_data, **kwargs):
        kwargs.setdefault('cached', False)
        kwargs.setdefault('error', False)
        self.assertLess(query_data['time_elapsed'], 1)
        query_data.pop('time_elapsed')
        self.assertEqual(query_data, kwargs)


class QueryAPITest(QueryAPITestCase):

    def test_not_logged_in(self):
        # TODO add more endpoints here
        endpoints = ['/api/query/1',
                     '/api/query_interactive/', '/api/database_explorer/']
        for resp in endpoints:
            response = self.client.get(resp)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response['location'],
                "http://testserver/accounts/login?next=%s" % (resp),
            )

    def test_invalid_query_id(self):
        """
        Test a 404 for query api
        """
        self.create_user()
        self.login()
        data = self.get_query(1)
        self.assert_query_data(
            data,
            error=True,
            data="No Query matches the given query."
        )

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
        self.assert_query_data(
            data,
            error=True,
            data='Query contained delete -- Can not be run'
        )

    def test_valid_query(self):
        user = self.create_user()
        query = QueryFactory(
            query_text="select id, username from auth_user",
            owner=user,
        )
        self.login()
        data = self.get_query(query.id)
        self.assert_query_data(data, data={
            'columns': ['id', 'username'],
            'data': [[user.id, user.username]],
        })

    def test_time(self):
        """
        Create query that returns a time stamp
        """
        user = self.create_user()
        query = QueryFactory(
            query_text="select now() as curr_time from auth_user limit 1",
            owner=user,
        )
        self.login()
        data = self.get_query(query.id)
        time_object = data['data']['data'][0][0]
        t = datetime.datetime.strptime(
            time_object, "%Y-%m-%dT%H:%M:%S"
        )

        # Time zone issues may be present
        delta_t = abs((datetime.datetime.now() - t).seconds) % 3600
        self.assertLess(delta_t, 2)

    def test_float(self):
        """
        Create query that returns a time stamp
        """
        user = self.create_user()
        query = QueryFactory(
            query_text="""select avg(val) avg_val from
            (
            (select 1.0  as val from auth_user limit 1)
            union
            (select 0.0  as val from auth_user limit 1)
            union
            (select 3.0  as val from auth_user limit 1)
            ) t1""",
            owner=user,
        )
        self.login()
        data = self.get_query(query.id)
        self.assert_query_data(data, data={
            u'columns': [u'avg_val'],
            u'data': [[1.33333]]
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
        self.assert_query_data(data, data={
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
                    date_joined > "<DT>"
                    and first_name = "<NAME>"
                limit
                    1
            """,
            owner=user,
        )
        defaults = []
        defaults.append(QueryDefaultFactory(
            query=query,
            search_for="<DT>",
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
        self.assert_query_data(data, data={
            'columns': ['first_name'],
            'data': [['John']],
        })

    def test_parameters_request(self):
        (user, query, defaults) = self.mock_valid_user_and_parameter_query()
        name = 'Bob'
        data = self.get_query(query.id, {'<NAME>': name})
        self.assert_query_data(data, data={
            'columns': ['first_name'],
            'data': [[name]],
        })


class QueryCacheTest(QueryAPITestCase):
    def setUp(self):
        self.user = self.create_user()
        self.login()

    def test_used_cache(self):
        """
        Runs query twice to see if caching goes from False to True
        """
        query = QueryFactory(
            query_text="select id, username from auth_user",
            owner=self.user,
        )
        data = self.get_query(query.id)
        # TODO make this run a longer query and validate the cache is faster
        self.assert_query_data(data, data={
            'columns': ['id', 'username'],
            'data': [[self.user.id, self.user.username]],
        })
        data = self.get_query(query.id)
        self.assert_query_data(data, cached=True, data={
            'columns': ['id', 'username'],
            'data': [[self.user.id, self.user.username]],
        })
        return query

    def test_no_cache_request(self):
        # Run Suite from before
        query = self.test_used_cache()
        # Now run with caching turned off
        # TODO use a url parameter in get here
        data = self.get_query(query.id, {'cacheable': "False"})
        self.assert_query_data(data, data={
            'columns': ['id', 'username'],
            'data': [[self.user.id, self.user.username]],
        })


class QueryPrecedentTest(QueryAPITestCase):
    def setUp(self):
        self.user = self.create_user()
        self.login()

    def test_precedent_query(self):
        # Create sub=query
        query_inner = QueryFactory(
            query_text="select id, username from auth_user",
            owner=self.user,
            title='inner'
        )
        query_outer = QueryFactory(
            query_text="show tables",  # """select * from <TABLE-%s>""" % (query_inner.id),
            owner=self.user,
            title='outer',
            db=query_inner.db
        )
        QueryPrecedentFactory(
            final_query=query_outer,
            preceding_query=query_inner
        )
        inner_data = self.get_query(query_inner.id)
        outer_data = self.get_query(query_outer.id)
        # Strip volatile data
        inner_data.pop('time_elapsed')
        outer_data.pop('time_elapsed')
        self.assertEqual(inner_data, outer_data)


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
