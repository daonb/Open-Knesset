
from django.conf.urls.defaults import *
from piston.resource import Resource
from django.views.decorators.cache import cache_page

from knesset.api.handlers import *

from resources import v2_api

# APIv1 piston-based code
CACHE_TIME = 60*15
vote_handler = cache_page(Resource(VoteHandler), CACHE_TIME)
bill_handler = cache_page(Resource(BillHandler), CACHE_TIME)
member_handler = cache_page(Resource(MemberHandler), CACHE_TIME)
party_handler = cache_page(Resource(PartyHandler), CACHE_TIME)
tag_handler = cache_page(Resource(TagHandler), CACHE_TIME)
agenda_handler = cache_page(Resource(AgendaHandler), CACHE_TIME)
committee_handler = cache_page(Resource(CommitteeHandler), CACHE_TIME)
committee_meeting_handler = cache_page(Resource(CommitteeMeetingHandler), CACHE_TIME)
event_handler = cache_page(Resource(EventHandler), CACHE_TIME)

urlpatterns = patterns('',
      # APIv1 code
      url(r'^vote/$', vote_handler, name='vote-handler'),
      url(r'^vote/(?P<id>[0-9]+)/$', vote_handler, name='vote-handler'),
      url(r'^bill/$', bill_handler, name='bill-handler'),
      url(r'^bill/(?P<id>[0-9]+)/$', bill_handler, name='bill-handler'),
      url(r'^member/$', member_handler, name='member-handler'),
      url(r'^member/(?P<id>[0-9]+)/$', member_handler, name='member-handler'),
      url(r'^party/$', party_handler, name='party-handler'),
      url(r'^party/(?P<id>[0-9]+)/$', party_handler, name='party-handler'),
      url(r'^tag/$', tag_handler, name='tag-handler'),
      url(r'^tag/(?P<id>[0-9]+)/$', tag_handler, name='tag-handler'),
      url(r'^tag/(?P<app_label>\w+)/(?P<object_type>\w+)/(?P<object_id>[0-9]+)/$', tag_handler, name='tag-handler'),
      url(r'^agenda/$', agenda_handler, name='agenda-handler'),
      url(r'^agenda/(?P<id>[0-9]+)/$', agenda_handler, name='agenda-handler'),
      url(r'^agenda/(?P<app_label>\w+)/(?P<object_type>\w+)/(?P<object_id>[0-9]+)/$', agenda_handler, name='agenda-handler'),
      url(r'^committee/$', committee_handler, name='committe-handler'),
      url(r'^committee/(?P<id>[0-9]+)/$', committee_handler, name='committe-handler'),
      url(r'^committeemeeting/$', committee_meeting_handler, name='committee-meeting-handler'),
      url(r'^committeemeeting/(?P<id>[0-9]+)/$', committee_meeting_handler, name='committee-meeting-handler'),
      url(r'^event/$', event_handler, name='event-handler'),
      url(r'^event/(?P<id>[0-9]+)/$', event_handler, name='event-handler'),
      # NOTE: this view is not in the api application, but in the events application
      url(r'^event/icalendar/$', 'knesset.events.views.icalendar', name='event-icalendar'),
      url(r'^event/icalendar/(?P<summary_length>\d+)/$', 'knesset.events.views.icalendar', name='event-icalendar'),
      # APIv2 code
      (r'^', include(v2_api.urls)),
      )

