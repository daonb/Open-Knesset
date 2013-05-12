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

MOTION_PUBLISHED, MOTION_FLAGGED, MOTION_REJECTED,\
MOTION_ACCEPTED, MOTION_APPEAL, MOTION_DELETED = range(6)
PUBLIC_MOTION_STATUS = ( MOTION_PUBLISHED, MOTION_ACCEPTED, MOTION_FLAGGED)

class MotionManager(models.Manager):
    '''MotionManager

    A class to hold some helpers methods for dealing with `Motion`
    '''

    def get_public(self):
        return self.filter(status__in=PUBLIC_MOTION_STATUS)

    def by_rank(self):
        return self.extra(select={
            'rank': '((100/%s*rating_score/(1+rating_votes+%s))+100)/2' % (Motion.rating.range, Motion.rating.weight)
            }).order_by('-rank')

    def summary(self, order='-rank'):
        return self.filter(status__in=PUBLIC_MOTION_STATUS).extra(select={
            'rank': '((100/%s*rating_score/(1+rating_votes+%s))+100)/2' % (Motion.rating.range, Motion.rating.weight)
            }).order_by(order)
        #TODO: rinse it so this will work
        return self.get_public().by_rank()


class Motion(models.Model):
    '''Motion is used to hold the phone book entry for each motion

        Fields:
            title - the title
            description - its description
            created - the time a motion was first connected to a committee
            modified - last time the status or the message was updated
            editor - the user that entered the data
            status - the current status
            log - a text log that keeps text messages for status changes
    '''

    creator = models.ForeignKey(User)
    editors = models.ManyToManyField(User, related_name='editing_motions', null=True, blank=True)
    title = models.CharField(max_length=60,
                             verbose_name = _('Title'))
    description = models.TextField(blank=True,
                                   verbose_name = _('Description'))
    status = models.IntegerField(choices = (
        (MOTION_PUBLISHED, _('published')),
        (MOTION_FLAGGED, _('flagged')),
        (MOTION_REJECTED, _('rejected')),
        (MOTION_ACCEPTED, _('accepted')),
        (MOTION_APPEAL, _('appeal')),
        (MOTION_DELETED, _('deleted')),
            ), default=MOTION_PUBLISHED)
    rating = RatingField(range=7, can_change_vote=True, allow_delete=True)
    links = generic.GenericRelation(Link, content_type_field="content_type",
       object_id_field="object_pk")
    events = generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    log = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = _('Motion')
        verbose_name_plural = _('Motions')

    @models.permalink
    def get_absolute_url(self):
        return ('motion-detail', [str(self.id)])

    def __unicode__(self):
        return self.title

    objects = MotionManager()

    def set_status(self, status, message=''):
       self.status = status
       self.log = '\n'.join((u'%s: %s' % (self.get_status_display(), datetime.now()),
                            u'\t%s' % message,
                            self.log,)
                           )
       self.save()

    def can_edit(self, user):
        return user.is_superuser or user==self.creator or \
               user in self.editors.all()
               
