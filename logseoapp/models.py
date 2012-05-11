# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from taggit.managers import TaggableManager
from django.db.models import Q, Avg, Count, F

class KwCntManager(models.Manager):
    def kw_count(self, keyword):
        return self.filter(phrase__icontains=keyword).count()

class Kw(models.Model):
    id = models.IntegerField(primary_key=True)
    phrase = models.CharField(max_length=765)
    tags = TaggableManager()
    objects = KwCntManager()

    #def num_ips(self):
        #num_ips = LogSeRank.objects.filter(phrase_id=self.id).annotate(num_books=Count('ip'))
        #return num_ips

    class Meta:
        db_table = u'kws'

    def __unicode__(self):
        return self.phrase

class Engine(models.Model):
    id = models.IntegerField(primary_key=True)
    engine = models.CharField(max_length=765)
    class Meta:
        db_table = u'engines'

    def __unicode__(self):
        return self.engine

class Page(models.Model):
    id = models.IntegerField(primary_key=True)
    page = models.CharField(max_length=765)
    class Meta:
        db_table = u'pages'

    def __unicode__(self):
        return self.page

class LogSeRankCntManager(models.Manager):
    def ip_count(self, id):
        return self.values('phrase_id').filter( position__gt = 0 ).annotate(num_ips=Count('ip', distinct = True),
                num_rank=Count('position'), avg_rank=Avg('position'))[:10]
"""
class LogSeRankAdmin(UserAdmin):
    list_filter = ('kw__phrase',)
"""
class LogSeRank(models.Model):
    id = models.IntegerField(primary_key=True)
    ip = models.IntegerField()
    position = models.IntegerField()
    phrase_id = models.ForeignKey('Kw',db_column='phrase_id')
    page_id = models.ForeignKey('Page',db_column='page_id')
    engine_id = models.ForeignKey('Engine',db_column='engine_id')
    http = models.TextField()
    refdate = models.CharField(max_length=765)
    reftime = models.CharField(max_length=765)
    objects = LogSeRankCntManager()
    class Meta:
        db_table = u'log_se_rank'



class RanksPagesDatesEngines(models.Model):
    phrase = models.CharField(max_length=765, blank=True)
    sengines = models.CharField(max_length=1023, blank=True)
    ipcount = models.BigIntegerField(null=True, blank=True)
    rank = models.TextField(blank=True)
    page = models.CharField(max_length=1023, blank=True)
    refdate = models.CharField(max_length=1023, blank=True)
    class Meta:
        db_table = u'ranks_pages_dates_engines'

