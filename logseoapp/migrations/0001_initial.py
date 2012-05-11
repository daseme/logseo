# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Knight'
        db.create_table('logseoapp_knight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('of_the_round_table', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('logseoapp', ['Knight'])

        # Adding model 'Engines'
        db.create_table(u'engines', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('engine', self.gf('django.db.models.fields.CharField')(max_length=765)),
        ))
        db.send_create_signal('logseoapp', ['Engines'])

        # Adding model 'Kws'
        db.create_table(u'kws', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('phrase', self.gf('django.db.models.fields.CharField')(max_length=765)),
        ))
        db.send_create_signal('logseoapp', ['Kws'])

        # Adding model 'LogSeRank'
        db.create_table(u'log_se_rank', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.IntegerField')()),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('phrase_id', self.gf('django.db.models.fields.IntegerField')()),
            ('page_id', self.gf('django.db.models.fields.IntegerField')()),
            ('engine_id', self.gf('django.db.models.fields.IntegerField')()),
            ('http', self.gf('django.db.models.fields.TextField')()),
            ('refdate', self.gf('django.db.models.fields.CharField')(max_length=765)),
            ('reftime', self.gf('django.db.models.fields.CharField')(max_length=765)),
        ))
        db.send_create_signal('logseoapp', ['LogSeRank'])

        # Adding model 'Pages'
        db.create_table(u'pages', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=765)),
        ))
        db.send_create_signal('logseoapp', ['Pages'])

        # Adding model 'RanksPagesDatesEngines'
        db.create_table(u'ranks_pages_dates_engines', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phrase', self.gf('django.db.models.fields.CharField')(max_length=765, blank=True)),
            ('sengines', self.gf('django.db.models.fields.CharField')(max_length=1023, blank=True)),
            ('ipcount', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('rank', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=1023, blank=True)),
            ('refdate', self.gf('django.db.models.fields.CharField')(max_length=1023, blank=True)),
        ))
        db.send_create_signal('logseoapp', ['RanksPagesDatesEngines'])


    def backwards(self, orm):
        
        # Deleting model 'Knight'
        db.delete_table('logseoapp_knight')

        # Deleting model 'Engines'
        db.delete_table(u'engines')

        # Deleting model 'Kws'
        db.delete_table(u'kws')

        # Deleting model 'LogSeRank'
        db.delete_table(u'log_se_rank')

        # Deleting model 'Pages'
        db.delete_table(u'pages')

        # Deleting model 'RanksPagesDatesEngines'
        db.delete_table(u'ranks_pages_dates_engines')


    models = {
        'logseoapp.engines': {
            'Meta': {'object_name': 'Engines', 'db_table': "u'engines'"},
            'engine': ('django.db.models.fields.CharField', [], {'max_length': '765'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'logseoapp.knight': {
            'Meta': {'object_name': 'Knight'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'of_the_round_table': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'logseoapp.kws': {
            'Meta': {'object_name': 'Kws', 'db_table': "u'kws'"},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.logserank': {
            'Meta': {'object_name': 'LogSeRank', 'db_table': "u'log_se_rank'"},
            'engine_id': ('django.db.models.fields.IntegerField', [], {}),
            'http': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IntegerField', [], {}),
            'page_id': ('django.db.models.fields.IntegerField', [], {}),
            'phrase_id': ('django.db.models.fields.IntegerField', [], {}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'refdate': ('django.db.models.fields.CharField', [], {'max_length': '765'}),
            'reftime': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.pages': {
            'Meta': {'object_name': 'Pages', 'db_table': "u'pages'"},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.rankspagesdatesengines': {
            'Meta': {'object_name': 'RanksPagesDatesEngines', 'db_table': "u'ranks_pages_dates_engines'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipcount': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '1023', 'blank': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '765', 'blank': 'True'}),
            'rank': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'refdate': ('django.db.models.fields.CharField', [], {'max_length': '1023', 'blank': 'True'}),
            'sengines': ('django.db.models.fields.CharField', [], {'max_length': '1023', 'blank': 'True'})
        }
    }

    complete_apps = ['logseoapp']
