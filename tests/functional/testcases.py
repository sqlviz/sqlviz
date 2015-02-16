from django.test import (LiveServerTestCase as BaseLiveServerTestCase,
                         TransactionTestCase)
from splinter import Browser

from ..factories import UserFactory


class TestCaseMixin(object):

    username = "username"
    password = "password"

    def create_user(self, **kwargs):
        attrs = {
            'username': self.username,
            'password': self.password,
        }
        attrs.update(kwargs)
        return UserFactory(**attrs)


class APITestCase(TestCaseMixin, TransactionTestCase):

    def login(self):
        self.client.login(username=self.username, password=self.password)


class LiveServerTestCase(TestCaseMixin, BaseLiveServerTestCase):

    """Base test case for in-browser functional tests."""

    initial_url = None
    login_button_value = 'Log in'

    def login(self):
        self.browser.fill('username', self.username)
        self.browser.fill('password', self.password)
        self.browser.find_by_value(self.login_button_value).click()

    def create_staff_user(self, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return super(LiveServerTestCase, self).create_user(**kwargs)

    def setUp(self):
        self.browser = Browser('django')
        if self.initial_url is not None:
            self.browser.visit("{}{}".format(
                self.live_server_url,
                self.initial_url,
            ))

    def tearDown(self):
        self.browser.quit()
