from django.test import TestCase

class LogSeoViewsTestCase(TestCase):
    def test_get_ranks(self):
        resp = self.client.get('/ranks/')
        self.assertEqual(resp.status_code, 200)
