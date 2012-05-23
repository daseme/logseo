import datetime
from haystack.indexes import *
from haystack import site
from logseoapp.models import Kw


class KWIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    phrase = CharField()



    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Kw.objects.all()

site.register(Kw, KWIndex)
