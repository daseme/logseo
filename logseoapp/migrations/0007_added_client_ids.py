# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'RanksPagesDatesEngines'
        db.delete_table(u'ranks_pages_dates_engines')

        # Adding model 'Client'
        db.create_table('logseoapp_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=765)),
            ('date_added', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal('logseoapp', ['Client'])

        # Adding field 'LogSeRank.client_id'
        db.add_column(u'log_se_rank', 'client_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['logseoapp.Client'], db_column='client_id'), keep_default=False)

        # Adding field 'Page.client_id'
        db.add_column(u'pages', 'client_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['logseoapp.Client'], db_column='client_id'), keep_default=False)

        # Adding field 'Kw.client_id'
        db.add_column(u'kws', 'client_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['logseoapp.Client'], db_column='client_id'), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'RanksPagesDatesEngines'
        db.create_table(u'ranks_pages_dates_engines', (
            ('sengines', self.gf('django.db.models.fields.CharField')(max_length=1023, blank=True)),
            ('phrase', self.gf('django.db.models.fields.CharField')(max_length=765, blank=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=1023, blank=True)),
            ('refdate', self.gf('django.db.models.fields.CharField')(max_length=1023, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rank', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ipcount', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('logseoapp', ['RanksPagesDatesEngines'])

        # Deleting model 'Client'
        db.delete_table('logseoapp_client')

        # Deleting field 'LogSeRank.client_id'
        db.delete_column(u'log_se_rank', 'client_id')

        # Deleting field 'Page.client_id'
        db.delete_column(u'pages', 'client_id')

        # Deleting field 'Kw.client_id'
        db.delete_column(u'kws', 'client_id')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'logseoapp.client': {
            'Meta': {'object_name': 'Client'},
            'date_added': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.engine': {
            'Meta': {'object_name': 'Engine', 'db_table': "u'engines'"},
            'engine': ('django.db.models.fields.CharField', [], {'max_length': '765'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'logseoapp.kw': {
            'Meta': {'object_name': 'Kw', 'db_table': "u'kws'"},
            'client_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Client']", 'db_column': "'client_id'"}),
            'first_seen': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.logserank': {
            'Meta': {'object_name': 'LogSeRank', 'db_table': "u'log_se_rank'"},
            'client_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Client']", 'db_column': "'client_id'"}),
            'engine_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Engine']", 'db_column': "'engine_id'"}),
            'http': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IntegerField', [], {}),
            'page_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Page']", 'db_column': "'page_id'"}),
            'phrase_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Kw']", 'db_column': "'phrase_id'"}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'refdate': ('django.db.models.fields.CharField', [], {'max_length': '765'}),
            'reftime': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.page': {
            'Meta': {'object_name': 'Page', 'db_table': "u'pages'"},
            'client_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Client']", 'db_column': "'client_id'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['logseoapp']
