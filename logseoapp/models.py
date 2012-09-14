# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from django.forms import ModelForm
from taggit.managers import TaggableManager
from django.db.models import Avg, Count


class Client(models.Model):

    name       = models.CharField(max_length=765)
    date_added = models.DateField(null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'logseoapp_client'


class ClientForm(ModelForm):
    class Meta:
        model = Client


class KwCntManager(models.Manager):
    def kw_count(self, keyword):
        return self.filter(phrase__icontains=keyword).count()


class Kw(models.Model):

    phrase     = models.CharField(max_length=765)
    first_seen = models.DateField(null=True)
    last_seen  = models.DateField(null=True)
    client_id  = models.ForeignKey('Client', db_column='client_id')
    tags       = TaggableManager()

    class Meta:
        db_table = u'logseoapp_kws'

    def __unicode__(self):
        return self.phrase


class Engine(models.Model):

    engine   = models.CharField(max_length=765)

    class Meta:
        db_table = u'logseoapp_engines'

    def __unicode__(self):
        return self.engine


class Page(models.Model):

    page       = models.CharField(max_length=765)
    client_id  = models.ForeignKey('Client', db_column='client_id')

    class Meta:
        db_table = u'logseoapp_pages'

    def __unicode__(self):
        return self.page


class LogSeRankCntManager(models.Manager):
    def ip_count(self, id):
        return self.values('phrase_id') \
                   .filter(position__gt=0) \
                   .annotate(num_ips=Count('ip', distinct=True),
                             num_rank=Count('position'),
                             avg_rank=Avg('position'))[:10]
"""
class LogSeRankAdmin(UserAdmin):
    list_filter = ('kw__phrase',)
"""


class LogSeRank(models.Model):

    ip = models.IntegerField()
    position = models.IntegerField()
    phrase_id = models.ForeignKey('Kw', db_column='phrase_id')
    page_id = models.ForeignKey('Page', db_column='page_id')
    engine_id = models.ForeignKey('Engine', db_column='engine_id')
    client_id  = models.ForeignKey('Client', db_column='client_id')
    http = models.TextField()
    refdate = models.CharField(max_length=765)
    reftime = models.CharField(max_length=765)
    objects = LogSeRankCntManager()

    class Meta:
        db_table = u'logseoapp_log_se_rank'
