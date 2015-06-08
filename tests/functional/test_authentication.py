from .testcases import LiveServerTestCase


class AdminLoginTest(LiveServerTestCase):

    initial_url = "/admin/"

    def test_invalid_username(self):
        """Ensure error shown when logging in with an invalid username."""
        assert not self.browser.find_by_css('.errornote')
        self.login()
        assert "case-sensitive" in \
            self.browser.find_by_css('.alert-danger').text

    def test_incorrect_password(self):
        """Ensure error shown when logging in with an incorrect password."""
        assert not self.browser.find_by_css('.alert-danger')
        self.create_user(is_staff=True, password="other password")
        self.login()
        assert "case-sensitive" in \
            self.browser.find_by_css('.alert-danger').text

    def test_valid_credentials(self):
        """Ensure logging in with valid credentials redirects to admin."""
        assert "Log out" not in self.browser.find_by_css('body').text
        self.create_user(is_staff=True)
        self.login()
        assert "Log out" in self.browser.find_by_css('body').text


class LoginPageTest(LiveServerTestCase):

    initial_url = "/accounts/login"
    login_button_value = 'Login'

    def assertDoesNotHaveErrors(self):
        assert not self.browser.find_by_css('.alert-danger')

    def assertHasErrors(self):
        assert "case-sensitive" in self.browser.find_by_css(
            '.alert-danger').text

    def test_invalid_username(self):
        """Ensure error shown when logging in with an invalid username."""
        self.assertDoesNotHaveErrors()
        self.login()
        self.assertHasErrors()

    def test_incorrect_password(self):
        """Ensure error shown when logging in with an incorrect password."""
        self.assertDoesNotHaveErrors()
        self.create_user(password="other password")
        self.login()
        self.assertHasErrors()

    def test_valid_credentials(self):
        """Ensure logging in with valid credentials redirects to admin."""
        assert "Interactive Mode" not in self.browser.find_by_css('body').text
        self.create_user()
        self.login()
        assert "Interactive Mode" not in self.browser.find_by_css('body').text
        assert ("No Queries or Dashboards are available" in
                self.browser.find_by_css('body').text)
        assert "Admin" not in self.browser.find_by_css('body').text

    def test_valid_credentials_not_staff(self):
        """Ensure logging in with valid credentials redirects to admin."""
        assert "Interactive Mode" not in self.browser.find_by_css('body').text
        self.create_user(is_staff=True)
        self.login()
        assert "Interactive Mode" in self.browser.find_by_css('body').text
        assert "Admin" in self.browser.find_by_css('body').text
