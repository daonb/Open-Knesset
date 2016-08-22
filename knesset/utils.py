# encoding: utf-8
from datetime import datetime
import re

from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.comments.views.comments import post_comment
from django.http import HttpResponse
from django.test import Client
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.http import Http404
from django.shortcuts import get_object_or_404
import django.contrib.comments.views.moderation as moderation
from django.utils.encoding import smart_str, smart_unicode
from django.conf import settings
from mailer import send_html_mail
from actstream.models import Action
import traceback
import hashlib


def limit_by_request(qs, request):
    if 'num' in request.GET:
        num = int(request.GET['num'])
        page = 'page' in request.GET and int(request.GET['page']) or 0
        return qs[page * num:(page + 1) * num]
    return qs


def yearstart(year):
    return datetime(year, 1, 1)


def yearend(year):
    return datetime(year, 12, 31)


def slugify_name(name):
    s = smart_str(name).replace("'", '"').replace(' ', '-')
    if isinstance(name, unicode):
        return s.decode('utf8')
    return s


def comment_post_wrapper(request):
    # Clean the request to prevent form spoofing
    if request.user.is_authenticated():
        if (('name' in request.POST and (request.user.get_full_name() != request.POST['name'])) or \
                    ('email' in request.POST and (request.user.email == request.POST['email']))):
            return HttpResponse("Access denied")
        return post_comment(request)
    return HttpResponse("Access denied")


@login_required
def delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.user or request.user.is_staff:
        return moderation.delete(request, comment_id)
    else:
        raise Http404


shitty_chars = [u'\u200e', u'\u200f', u'\u202a', u'\u202b', u'\u202c', u'\u202d', u'\u202e', u'\u201d', u'\u2013']
trans = dict([(ord(chr), None) for chr in shitty_chars])

trans_clean = trans.copy()
trans_clean[96] = None
for c in ':0123456789(),-"\'':
    trans_clean[ord(c)] = None


def clean_string(s):
    if isinstance(s, unicode):
        s = s.translate(trans)
    else:
        s = s.replace('\xe2\x80\x9d', '').replace('\xe2\x80\x93', '')
    return s


def cannonize(s):
    s = clean_string(s)
    s = s.replace('&nbsp', ' ').replace('gt;', '').replace('\n', '')
    s = re.sub("""\d{4,4}""", '', s)
    return re.sub("""["'`\(\) /.,\-\xa0]""", '', s)  # @IndentOk


try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps
import inspect


def disable_for_loaddata(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        for fr in inspect.stack():
            if inspect.getmodulename(fr[1]) in ('loaddata', 'sync_dev'):
                return
        signal_handler(*args, **kwargs)

    return wrapper


class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.

    """

    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)


def notify_responsible_adult(msg):
    """Send an email to some responsible adult(s)"""
    adults = getattr(settings, 'RESPONSIBLE_ADULTS', None)
    if adults:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'email@example.com')
        send_html_mail(_('Open Knesset requires attention'), msg, msg, from_email, adults)


def main_actions():
    """
    Actions used for main view latests actions and for /feeds/main
    """
    return Action.objects.filter(verb__in=['comment-added', 'annotated']) \
        .order_by('-timestamp') \
        .prefetch_related('target')


def reverse_with_query(viewname, args=None, kwargs=None, query_kwargs=None):
    """
    Custom reverse to add a query string after the url
    Example usage:
    url = my_reverse('my_test_url', kwargs={'pk': object.id}, query_kwargs={'next': reverse('home')})
    """
    requested_url = reverse(viewname, args=None, kwargs=kwargs)

    if query_kwargs:
        return u'{0}?{1}'.format(requested_url, urlencode(query_kwargs))

    return requested_url


def send_chat_notification(file, text, data):
    from django_slack import slack_message
    text = ("{text}\n{data}\n-- {file}").format(file=file, text=text, data=data)
    if getattr(settings, 'SLACK_BACKEND', None) in (None, 'django_slack.backends.DisabledBackend'):
        print "-- SLACK MESSAGE"
        print text
        print "----"
    else:
        slack_message('django-slack/text.slack', {"text": text})


def send_chat_exception_notification(file, text_prefix, data, exception):
    data.update({'traceback': traceback.format_exc()})
    send_chat_notification(file, text_prefix + " " + str(exception.message), data)


def get_thousands_string(f):
    """
    Get a nice string representation of a field of 1000's of NIS, which is int or None.
    """
    if f is None:
        return "N/A"
    elif f == 0:
        return "0 NIS"
    else:
        return "%d000 NIS" % f


def get_cache_key(str):
    str = str.encode('utf-8')
    return hashlib.sha1(str).hexdigest()
