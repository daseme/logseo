from datetime import datetime
from django.test import TestCase
from logseoapp.models import Kws,Engines,Pages,LogSeRank

class LogSeoViewsTestCase(TestCase):
    """
    test getting /ranks/
    """
    fixtures = ['fixtures/logseoapp_views_testdata.json']

    def test_get_ranks(self):

        resp = self.client.get('/ranks/')
        self.assertEqual(resp.status_code, 200)
