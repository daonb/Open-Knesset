#encoding: UTF-8
from django.conf.urls.defaults import url, patterns
from djangoratings.views import AddRatingFromModel

from .views import (
    CommitteeMeeting, CommitteeListView, CommitteeDetailView,
    MeetingListView, MeetingDetailView, meeting_list_by_date,
    MeetingTagListView)


meeting_list = MeetingListView.as_view(
    queryset=CommitteeMeeting.objects.all(), paginate_by=20)

committeesurlpatterns = patterns('',
    url(r'^committee/$', CommitteeListView.as_view(), name='committee-list'),
    url(r'^committee/(?P<pk>\d+)/$', CommitteeDetailView.as_view(), name='committee-detail'),
    url(r'^committee/(?P<committee_id>\d+)/all_meetings/$', meeting_list, name='committee-all-meetings'),
    url(r'^committee/(?P<committee_id>\d+)/date/(?P<date>[\d\-]+)/$', meeting_list_by_date, name='committee-meetings-by-date'),
    url(r'^committee/(?P<committee_id>\d+)/date/$', meeting_list_by_date, name='committee-meetings-by-date'),
    url(r'^committee/meeting/(?P<pk>\d+)/$', MeetingDetailView.as_view(), name='committee-meeting'),
    url(r'^committee/meeting/tag/(?P<tag>.*)/$', MeetingTagListView.as_view(),
        name='committeemeeting-tag'),
)
