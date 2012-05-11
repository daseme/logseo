# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Kws'
        db.delete_table(u'kws')

        # Deleting model 'Pages'
        db.delete_table(u'pages')

        # Deleting model 'Engines'
        db.delete_table(u'engines')

        # Adding model 'Page'
        db.create_table(u'pages', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=765)),
        ))
        db.send_create_signal('logseoapp', ['Page'])

        # Adding model 'Engine'
        db.create_table(u'engines', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('engine', self.gf('django.db.models.fields.CharField')(max_length=765)),
        ))
        db.send_create_signal('logseoapp', ['Engine'])

        # Adding model 'Kw'
        db.create_table(u'kws', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('phrase', self.gf('django.db.models.fields.CharField')(max_length=765)),
        ))
        db.send_create_signal('logseoapp', ['Kw'])

        # Changing field 'LogSeRank.phrase_id'
        db.alter_column(u'log_se_rank', 'phrase_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['logseoapp.Kw'], db_column='phrase_id'))

        # Adding index on 'LogSeRank', fields ['phrase_id']
        db.create_index(u'log_se_rank', ['phrase_id'])

        # Changing field 'LogSeRank.engine_id'
        db.alter_column(u'log_se_rank', 'engine_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['logseoapp.Engine'], db_column='engine_id'))

        # Adding index on 'LogSeRank', fields ['engine_id']
        db.create_index(u'log_se_rank', ['engine_id'])

        # Changing field 'LogSeRank.page_id'
        db.alter_column(u'log_se_rank', 'page_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['logseoapp.Page'], db_column='page_id'))

        # Adding index on 'LogSeRank', fields ['page_id']
        db.create_index(u'log_se_rank', ['page_id'])


    def backwards(self, orm):
        
        # Removing index on 'LogSeRank', fields ['page_id']
        db.delete_index(u'log_se_rank', ['page_id'])

        # Removing index on 'LogSeRank', fields ['engine_id']
        db.delete_index(u'log_se_rank', ['engine_id'])

        # Removing index on 'LogSeRank', fields ['phrase_id']
        db.delete_index(u'log_se_rank', ['phrase_id'])

        # Adding model 'Kws'
        db.create_table(u'kws', (
            ('phrase', self.gf('django.db.models.fields.CharField')(max_length=765)),
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
        ))
        db.send_create_signal('logseoapp', ['Kws'])

        # Adding model 'Pages'
        db.create_table(u'pages', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=765)),
        ))
        db.send_create_signal('logseoapp', ['Pages'])

        # Adding model 'Engines'
        db.create_table(u'engines', (
            ('engine', self.gf('django.db.models.fields.CharField')(max_length=765)),
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
        ))
        db.send_create_signal('logseoapp', ['Engines'])

        # Deleting model 'Page'
        db.delete_table(u'pages')

        # Deleting model 'Engine'
        db.delete_table(u'engines')

        # Deleting model 'Kw'
        db.delete_table(u'kws')

        # Changing field 'LogSeRank.phrase_id'
        db.alter_column(u'log_se_rank', 'phrase_id', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'LogSeRank.engine_id'
        db.alter_column(u'log_se_rank', 'engine_id', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'LogSeRank.page_id'
        db.alter_column(u'log_se_rank', 'page_id', self.gf('django.db.models.fields.IntegerField')())


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'logseoapp.engine': {
            'Meta': {'object_name': 'Engine', 'db_table': "u'engines'"},
            'engine': ('django.db.models.fields.CharField', [], {'max_length': '765'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'logseoapp.kw': {
            'Meta': {'object_name': 'Kw', 'db_table': "u'kws'"},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.logserank': {
            'Meta': {'object_name': 'LogSeRank', 'db_table': "u'log_se_rank'"},
            'engine_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Engine']", 'db_column': "'engine_id'"}),
            'http': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IntegerField', [], {}),
            'page_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Page']", 'db_column': "'page_id'"}),
            'phrase_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['logseoapp.Kw']", 'db_column': "'phrase_id'"}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'refdate': ('django.db.models.fields.CharField', [], {'max_length': '765'}),
            'reftime': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.page': {
            'Meta': {'object_name': 'Page', 'db_table': "u'pages'"},
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
