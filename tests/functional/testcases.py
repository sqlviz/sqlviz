from django.test import LiveServerTestCase, TransactionTestCase
from splinter import Browser

from ..factories import UserFactory


class APITestCase(TransactionTestCase):

    username = "username"
    password = "password"

    def login(self):
        self.client.login(username=self.username, password=self.password)

    def create_user(self, **defaults):
        kwargs = {
            'username': self.username,
            'password': self.password,
        }
        kwargs.update(defaults)
        return UserFactory(**kwargs)


class TestCase(LiveServerTestCase):

    """Base test case for in-browser functional tests."""

    initial_url = None

    def setUp(self):
        self.browser = Browser('django')
        if self.initial_url is not None:
            self.browser.visit("{}{}".format(
                self.live_server_url,
                self.initial_url,
            ))

    def tearDown(self):
        self.browser.quit()
