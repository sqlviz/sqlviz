from django.test import LiveServerTestCase
from splinter import Browser


class TestCase(LiveServerTestCase):

    """Base test case for in-browser functional tests."""

    def setUp(self):
        self.browser = Browser('django')

    def tearDown(self):
        self.browser.quit()
