from datetime import datetime, date, timedelta
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User,Group,Permission
from django.contrib.contenttypes.models import ContentType
from annotatetext.models import Annotation
from actstream.models import Action
from tagging.models import Tag, TaggedItem
from laws.models import Bill
from mks.models import Member, Knesset
from links.models import LinkType
from models import Committee, CommitteeMeeting

just_id = lambda x: x.id
APP = 'committees'

class CommitteeMeetingDetailViewTest(TestCase):

    def setUp(self):
        self.knesset = Knesset.objects.create(number=1,
                            start_date=datetime.today()-timedelta(days=1))
        self.committee_1 = Committee.objects.create(name='c1')
        self.committee_2 = Committee.objects.create(name='c2')
        self.meeting_1 = self.committee_1.meetings.create(date=datetime.now(),
                                 protocol_text='''jacob:
I am a perfectionist
adrian:
I have a deadline''')
        self.meeting_1.create_protocol_parts()
        self.meeting_2 = self.committee_1.meetings.create(date=datetime.now(),
                                                         protocol_text='m2')
        self.meeting_2.create_protocol_parts()
        self.jacob = User.objects.create_user('jacob', 'jacob@example.com',
                                              'JKM')
        self.adrian = User.objects.create_user('adrian', 'adrian@example.com',
                                              'ADRIAN')
        (self.group, created) = Group.objects.get_or_create(name='Valid Email')
        if created:
            self.group.save()
        self.group.permissions.add(Permission.objects.get(name='Can add annotation'))
        self.jacob.groups.add(self.group)

        ct = ContentType.objects.get_for_model(Tag)
        self.adrian.user_permissions.add(Permission.objects.get(codename='add_tag', content_type=ct))

        self.bill_1 = Bill.objects.create(stage='1', title='bill 1')
        self.mk_1 = Member.objects.create(name='mk 1')
        self.motion = self.committee_1.motions.create(creator=self.jacob,
                                                title="hello", description="hello world")
        self.tag_1 = Tag.objects.create(name='tag1')
        # self.knesset = Knesset.objects.create(start_date=date(1970,1,1), end_date=date(2020,1,1))
        self.meeting_1.mks_attended.add(self.mk_1)

    def testProtocolPart(self):
        parts_list = self.meeting_1.parts.list()
        self.assertEqual(parts_list.count(), 2)
        self.assertEqual(parts_list[0].header, u'jacob')
        self.assertEqual(parts_list[0].body, 'I am a perfectionist')
        self.assertEqual(parts_list[1].header, u'adrian')
        self.assertEqual(parts_list[1].body, 'I have a deadline')

    def testPartAnnotation(self):
        '''this is more about testing the annotatext app '''
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        part = self.meeting_1.parts.list()[0]
        res = self.client.post(reverse('annotatetext-post_annotation'),
                        {'selection_start': 7,
                         'selection_end': 14,
                         'flags': 0,
                         'color': '#000',
                         'lengthcheck': len(part.body),
                         'comment' : 'just perfect',
                         'object_id': part.id,
                         'content_type': ContentType.objects.get_for_model(part).id,
                        })
        self.assertEqual(res.status_code, 302)
        annotation = Annotation.objects.get(object_id=part.id,
                         content_type=ContentType.objects.get_for_model(part).id)
        self.assertEqual(annotation.selection, 'perfect')
        # ensure the activity has been recorded
        stream = Action.objects.stream_for_actor(self.jacob)
        self.assertEqual(stream.count(), 3)
        self.assertEqual(stream[0].verb, 'started following')
        self.assertEqual(stream[0].target.id, self.meeting_1.id)
        self.assertEqual(stream[1].verb, 'got badge')
        self.assertEqual(stream[2].verb, 'annotated')
        self.assertEqual(stream[2].target.id, annotation.id)
        # ensure we will see it on the committee page
        annotations = self.committee_1.annotations
        self.assertEqual(annotations.count(), 1)
        self.assertEqual(annotations[0].comment, 'just perfect')
        # test the deletion of an annotation
        annotation.delete()
        stream = Action.objects.stream_for_actor(self.jacob)
        self.assertEqual(stream.count(), 2)

    def testTwoAnnotations(self):
        '''create two annotations on same part, and delete them'''
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        part = self.meeting_1.parts.list()[0]
        res = self.client.post(reverse('annotatetext-post_annotation'),
                        {'selection_start': 7,
                         'selection_end': 14,
                         'flags': 0,
                         'color': '#000',
                         'lengthcheck': len(part.body),
                         'comment' : 'just perfect',
                         'object_id': part.id,
                         'content_type': ContentType.objects.get_for_model(part).id,
                        })
        self.assertEqual(res.status_code, 302)
        res = self.client.post(reverse('annotatetext-post_annotation'),
                        {'selection_start': 8,
                         'selection_end': 15,
                         'flags': 0,
                         'color': '#000',
                         'lengthcheck': len(part.body),
                         'comment' : 'not quite',
                         'object_id': part.id,
                         'content_type': ContentType.objects.get_for_model(part).id,
                        })
        self.assertEqual(res.status_code, 302)

        annotations = Annotation.objects.filter(object_id=part.id,
                         content_type=ContentType.objects.get_for_model(part).id)
        self.assertEqual(annotations.count(), 2)
        # ensure we will see it on the committee page
        c_annotations = self.committee_1.annotations
        self.assertEqual(c_annotations.count(), 2)
        self.assertEqual(c_annotations[0].comment, 'just perfect')
        self.assertEqual(c_annotations[1].comment, 'not quite')
        # test the deletion of an annotation
        annotations[0].delete()
        c_annotations = self.committee_1.annotations
        self.assertEqual(c_annotations.count(), 1)

    def testAnnotationForbidden(self):
        self.jacob.groups.clear() # invalidate this user's email
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        part = self.meeting_1.parts.list()[0]
        res = self.client.post(reverse('annotatetext-post_annotation'),
                        {'selection_start': 7,
                         'selection_end': 14,
                         'flags': 0,
                         'color': '#000',
                         'lengthcheck': len(part.body),
                         'comment' : 'just perfect',
                         'object_id': part.id,
                         'content_type': ContentType.objects.get_for_model(part).id,
                        })
        self.assertEqual(res.status_code, 403) # 403 Forbidden. 302 means a user with unverified email has posted an annotation. 

    def testCommitteeList(self):
        res = self.client.get(reverse('committee-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'committees/committee_list.html')
        committees = res.context['committees']
        self.assertEqual(map(just_id, committees),
                         [ self.committee_1.id, self.committee_2.id, ])
        self.assertQuerysetEqual(res.context['motions'],
                                 ["<Motion: hello>"])

    def testCommitteeMeetings(self):
        res = self.client.get(self.committee_1.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'committees/committee_detail.html')
        object_list = res.context['meetings_list']
        self.assertEqual(map(just_id, object_list),
                         [self.meeting_1.id, self.meeting_2.id, ],
                         'object_list has wrong objects: %s' % object_list)

    def test_committee_meeting(self):
        res = self.client.get(self.meeting_1.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'committees/committeemeeting_detail.html')
        members = res.context['members']
        self.assertEqual(map(just_id, members),
                         [self.mk_1.id],
                         'members has wrong objects: %s' % members)

    def testLoginRequired(self):
        res = self.client.post(reverse('committee-meeting',
                           kwargs={'pk': self.meeting_1.id}))
        self.assertFalse(self.bill_1 in self.meeting_1.bills_first.all())
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res['location'].startswith('%s%s'  %
                                       ('http://testserver', settings.LOGIN_URL)))

    def testConnectToMK(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('committee-meeting',
                           kwargs={'pk': self.meeting_1.id}),
                               {'user_input_type': 'mk',
                                'mk_name': self.mk_1.name})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(self.meeting_1 in self.mk_1.committee_meetings.all())
        self.client.logout()

    def testConnectToBill(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.post(reverse('committee-meeting',
                                       kwargs={'pk':
                                               self.meeting_1.id}),
                               {'user_input_type': 'bill',
                                'bill_id': self.bill_1.id})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(self.bill_1 in self.meeting_1.bills_first.all())
        self.client.logout()

    def test_add_tag_login_required(self):
        url = reverse('add-tag-to-object',
                                 kwargs={'app':APP,
                                         'object_type':'committeemeeting',
                                         'object_id': self.meeting_1.id})
        res = self.client.post(url, {'tag_id':self.tag_1})
        self.assertRedirects(res, "%s?next=%s" % (settings.LOGIN_URL, url),
                             status_code=302)

    def test_add_tag(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        url = reverse('add-tag-to-object',
                                 kwargs={'app':APP,
                                         'object_type': 'committeemeeting',
                                         'object_id': self.meeting_1.id})
        res = self.client.post(url, {'tag_id':self.tag_1.id})
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.tag_1, self.meeting_1.tags)

    def test_create_tag_permission_required(self):
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        url = reverse('create-tag',
                                 kwargs={'app':APP,
                                         'object_type': 'committeemeeting',
                                         'object_id': self.meeting_1.id})
        res = self.client.post(url, {'tag':'new tag'})
        self.assertRedirects(res, "%s?next=%s" % (settings.LOGIN_URL, url),
                             status_code=302)

    def test_create_tag(self):
        self.assertTrue(self.client.login(username='adrian',
                                          password='ADRIAN'))
        url = reverse('create-tag',
                                 kwargs={'app':APP,
                                         'object_type': 'committeemeeting',
                                         'object_id': self.meeting_1.id})
        res = self.client.post(url, {'tag':'new tag'})
        self.assertEqual(res.status_code, 200)
        self.new_tag = Tag.objects.get(name='new tag')
        self.assertIn(self.new_tag, self.meeting_1.tags)

    def test_committeemeeting_by_tag(self):
        self.ti = TaggedItem._default_manager.create(
            tag=self.tag_1,
            content_type=ContentType.objects.get_for_model(CommitteeMeeting),
            object_id=self.meeting_1.id)
        res = self.client.get(reverse('committeemeeting-tag', args=[self.tag_1.name]))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'committees/committeemeeting_list_by_tag.html')
        tag = res.context['tag']
        self.assertEqual(tag, self.tag_1)
        self.assertQuerysetEqual(res.context['object_list'],
                                 ['<CommitteeMeeting: c1 - None>'])
        # cleanup
        self.ti.delete()

    def tearDown(self):
        self.meeting_1.delete()
        self.meeting_2.delete()
        self.committee_1.delete()
        self.committee_2.delete()
        self.jacob.delete()
        self.group.delete()
        self.bill_1.delete()
        self.mk_1.delete()

