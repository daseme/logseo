# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'LogSeRank.id'
        db.alter_column(u'log_se_rank', 'id', self.gf('django.db.models.fields.AutoField')(primary_key=True))

        # Changing field 'Engine.id'
        db.alter_column(u'engines', 'id', self.gf('django.db.models.fields.AutoField')(primary_key=True))

        # Changing field 'Page.id'
        db.alter_column(u'pages', 'id', self.gf('django.db.models.fields.AutoField')(primary_key=True))


    def backwards(self, orm):
        
        # Changing field 'LogSeRank.id'
        db.alter_column(u'log_se_rank', 'id', self.gf('django.db.models.fields.IntegerField')(primary_key=True))

        # Changing field 'Engine.id'
        db.alter_column(u'engines', 'id', self.gf('django.db.models.fields.IntegerField')(primary_key=True))

        # Changing field 'Page.id'
        db.alter_column(u'pages', 'id', self.gf('django.db.models.fields.IntegerField')(primary_key=True))


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'logseoapp.kw': {
            'Meta': {'object_name': 'Kw', 'db_table': "u'kws'"},
            'first_seen': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '765'})
        },
        'logseoapp.logserank': {
            'Meta': {'object_name': 'LogSeRank', 'db_table': "u'log_se_rank'"},
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
