"""
from django.core.urlresolvers import reverse
from .testcases import LiveServerTestCase


TODO add test for each major url
class MLIndexTestCase(LiveServerTestCase):
    def test_url(self):
        url = reverse('ml:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
"""
