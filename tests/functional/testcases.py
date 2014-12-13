from django.test import LiveServerTestCase
from splinter import Browser


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
