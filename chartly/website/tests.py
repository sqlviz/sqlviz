from django.test import TestCase
import query
# Create your tests here.

class DataManagerTest(TestCase):

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently() should return False for polls whose
        pub_date is in the future
        """
        DM = DataManager(1)
        self.assertEqual(DM.query_id, 1)