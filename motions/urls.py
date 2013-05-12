#encoding: UTF-8
from django.conf.urls.defaults import url, patterns
from djangoratings.views import AddRatingFromModel

from .views import (MotionListView, MotionsMoreView,
    MotionDetailView, delete_motion, delete_motion_rating, edit_motion)

motionsurlpatterns = patterns('',
    url(r'^motion/$', MotionListView.as_view(), name='motion-list'),
    url(r'^motion/(?P<pk>\d+)/$', MotionDetailView.as_view(), name='motion-detail'),
    url(r'motion/add/$', edit_motion, name='add-motion'),
    url(r'^motion/edit/(?P<pk>\d+)/$', edit_motion, name='edit-motion'),
    url(r'^motion/delete/(?P<pk>\d+)/$', delete_motion, name='delete-motion'),
    url(r'^motion/rate/(?P<object_id>\d+)/(?P<score>\d+)/$',
        AddRatingFromModel(),
        {'app_label': 'motions', 'model': 'motion', 'field_name': 'rating'},
        name='rate-motion'),
    url(r'^motion/unrate/(?P<object_id>\d+)/$', delete_motion_rating,
        name='delete-motion-rating'),
)
