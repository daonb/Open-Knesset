# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Keyword', fields ['kw_text']
        db.create_unique(u'okhelptexts_keyword', ['kw_text'])


    def backwards(self, orm):
        # Removing unique constraint on 'Keyword', fields ['kw_text']
        db.delete_unique(u'okhelptexts_keyword', ['kw_text'])


    models = {
        u'okhelptexts.helptext': {
            'Meta': {'object_name': 'Helptext'},
            'fulltext': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moreinfo': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        u'okhelptexts.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'helptext': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['okhelptexts.Helptext']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kw_text': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        }
    }

    complete_apps = ['okhelptexts']