#encoding: UTF-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext
from knesset.annotations.handlers import AnnotationHandler
from piston.resource import Resource

annotation_resource = Resource(AnnotationHandler)

urlpatterns = patterns('',
    url(r'^(?P<id>[^/]+)/', annotation_resource),
    url(r'^$', annotation_resource),
    ) 