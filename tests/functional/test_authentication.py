from django.contrib.auth.models import User

from .testcases import TestCase


class AdminLoginTest(TestCase):

    username = "username"
    password = "password"
    initial_url = "/admin/"

    def login(self):
        self.browser.fill('username', self.username)
        self.browser.fill('password', self.password)
        self.browser.find_by_value('Log in').click()

    def test_invalid_username(self):
        """Ensure error shown when logging in with an invalid username."""
        assert not self.browser.find_by_css('.errornote')
        self.login()
        assert "case-sensitive" in self.browser.find_by_css('.errornote').text

    def test_incorrect_password(self):
        """Ensure error shown when logging in with an incorrect password."""
        User.objects.create_superuser(
            username=self.username,
            email="u@example.com",
            password="other password",
        )
        assert not self.browser.find_by_css('.errornote')
        self.login()
        assert "case-sensitive" in self.browser.find_by_css('.errornote').text

    def test_valid_credentials(self):
        """Ensure logging in with valid credentials redirects to admin."""
        User.objects.create_superuser(
            username=self.username,
            email="u@example.com",
            password=self.password,
        )
        assert "Log out" not in self.browser.find_by_css('body').text
        self.login()
        assert "Log out" in self.browser.find_by_css('body').text
