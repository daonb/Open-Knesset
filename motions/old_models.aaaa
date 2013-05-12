#encoding: utf-8
import re
import logging
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext

from tagging.models import Tag
from djangoratings.fields import RatingField

from events.models import Event
from links.models import Link

TOPIC_PUBLISHED, TOPIC_FLAGGED, TOPIC_REJECTED,\
TOPIC_ACCEPTED, TOPIC_APPEAL, TOPIC_DELETED = range(6)
PUBLIC_TOPIC_STATUS = ( TOPIC_PUBLISHED, TOPIC_ACCEPTED, TOPIC_FLAGGED)

class TopicManager(models.Manager):
    '''TopicManager

    A class to hold some helpers methods for dealing with `Topic`
    '''

    def get_public(self):
        return self.filter(status__in=PUBLIC_TOPIC_STATUS)

    def by_rank(self):
        return self.extra(select={
            'rank': '((100/%s*rating_score/(1+rating_votes+%s))+100)/2' % (Topic.rating.range, Topic.rating.weight)
            }).order_by('-rank')

    def summary(self, order='-rank'):
        return self.filter(status__in=PUBLIC_TOPIC_STATUS).extra(select={
            'rank': '((100/%s*rating_score/(1+rating_votes+%s))+100)/2' % (Topic.rating.range, Topic.rating.weight)
            }).order_by(order)
        #TODO: rinse it so this will work
        return self.get_public().by_rank()


class Topic(models.Model):
    '''Topic is used to hold the phone book entry for each topic

        Fields:
            title - the title
            description - its description
            created - the time a topic was first connected to a committee
            modified - last time the status or the message was updated
            editor - the user that entered the data
            status - the current status
            log - a text log that keeps text messages for status changes
    '''

    creator = models.ForeignKey(User)
    editors = models.ManyToManyField(User, related_name='editing_topics', null=True, blank=True)
    title = models.CharField(max_length=60,
                             verbose_name = _('Title'))
    description = models.TextField(blank=True,
                                   verbose_name = _('Description'))
    status = models.IntegerField(choices = (
        (TOPIC_PUBLISHED, _('published')),
        (TOPIC_FLAGGED, _('flagged')),
        (TOPIC_REJECTED, _('rejected')),
        (TOPIC_ACCEPTED, _('accepted')),
        (TOPIC_APPEAL, _('appeal')),
        (TOPIC_DELETED, _('deleted')),
            ), default=TOPIC_PUBLISHED)
    rating = RatingField(range=7, can_change_vote=True, allow_delete=True)
    links = generic.GenericRelation(Link, content_type_field="content_type",
       object_id_field="object_pk")
    events = generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    log = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
    @models.permalink
    def get_absolute_url(self):
        return ('topic-detail', [str(self.id)])

    def __unicode__(self):
        return _("%(title)s by %(creator)s") % self

    objects = TopicManager()

    def set_status(self, status, message=''):
       self.status = status
       self.log = '\n'.join((u'%s: %s' % (self.get_status_display(), datetime.now()),
                            u'\t%s' % message,
                            self.log,)
                           )
       self.save()

    def can_edit(self, user):
        return user==self.creator or user in self.editors.all()
