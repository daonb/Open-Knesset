"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.auth.models import User,Group,Permission
from django.contrib.auth.models import User,Group,Permission

from models import Topic

class TopicsTest(TestCase):

    def setUp(self):
        self.django = Site.objects.create(name='django', domain="djangoproject.com")
        self.python = Site.objects.create(name='python', domain="python.org")
        self.jacob = User.objects.create_user('jacob', 'jacob@example.com',
                                              'JKM')
        self.ofri = User.objects.create_user('ofri', 'ofri@example.com',
                                              'ofri')
        (self.group, created) = Group.objects.get_or_create(name='Valid Email')
        if created:
            self.group.save()
        self.group.permissions.add(Permission.objects.get(name='Can add Topic'))
        self.jacob.groups.add(self.group)
        self.topic = self.django.topic_set.create(creator=self.jacob,
                                                title="hello", description="hello world")
        self.topic2 = self.django.topic_set.create(creator=self.ofri,
                                                title="bye", description="goodbye")
        self.linktype = LinkType.objects.create(title='default')


    def testBasic(self):
        self.topic2.set_status(TOPIC_REJECTED, "just because")
        self.assertEqual(self.django.topic_set.get_public().count(), 1)
        self.assertEqual(Topic.objects.get_public().count(), 1)
        self.topic.set_status(TOPIC_REJECTED, "because I feel like it")
        self.assertEqual(self.django.topic_set.get_public().count(), 0)

    def testPermissions(self):
        self.assertTrue(self.topic.can_edit(self.jacob))
        self.assertFalse(self.topic.can_edit(self.ofri))
        self.topic.editors.add(self.ofri)
        self.assertTrue(self.topic.can_edit(self.ofri))
        self.topic.editors.remove(self.ofri)


    def test_edit_topic_form(self):
        res = self.client.get(reverse('edit-committee-topic',
                                 kwargs={'committee_id': self.django.id,
                                         'topic_id': self.topic.id}))
        self.assertEqual(res.status_code, 302) # login required
        self.assertTrue(self.client.login(username='ofri',
                                          password='ofri'))
        res = self.client.get(reverse('edit-committee-topic',
                                 kwargs={'committee_id': self.django.id,
                                         'topic_id': self.topic.id}))
        self.assertEqual(res.status_code, 403) # user is not an editor
        self.assertTrue(self.client.login(username='jacob',
                                          password='JKM'))
        res = self.client.get(reverse('edit-committee-topic',
                                 kwargs={'committee_id': self.django.id,
                                         'topic_id': self.topic.id}))
        self.assertEqual(res.status_code, 200) # user is an editor
        self.assertTemplateUsed(res, 'committees/edit_topic.html')

    def test_edit_topic_logged_required(self):
        res = self.client.post(reverse('edit-committee-topic',
                                 kwargs={'committee_id': self.django.id,
                                         'topic_id': self.topic.id}),
                               {'title':'test topic title',
                                'description': 'test topic description',
                                'committees':self.django.id,
                                'form-INITIAL_FORMS':0,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':3})
        self.assertEqual(res.status_code, 302) # redirect to login
        self.assertTrue(res['location'].startswith('%s%s'  %
                                       ('http://testserver', settings.LOGIN_URL)))

    def test_edit_topic(self):
        self.assertTrue(self.client.login(username='jacob',
                                          password='JKM'))
        res = self.client.post(reverse('edit-committee-topic',
                                 kwargs={'committee_id': self.django.id,
                                         'topic_id': self.topic.id}),
                               {'title':'test topic title',
                                'description': 'test topic description',
                                'committees':self.django.id,
                                'form-INITIAL_FORMS':0,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':3})
        self.assertEqual(res.status_code, 302) # redirect after POST
        t = Topic.objects.get(pk=self.topic.id)
        self.assertEqual(t.title, 'test topic title')
        self.assertEqual(t.description, 'test topic description')
        self.assertEqual(Topic.objects.count(), 2) # make sure we didn't create
                                                   # a new topic

    def test_add_topic(self):
        self.assertTrue(self.client.login(username='jacob',
                                          password='JKM'))
        res = self.client.post(reverse('edit-committee-topic',
                                 kwargs={'committee_id': self.django.id}),
                               {'title':'test topic title',
                                'description': 'test topic description',
                                'committees':self.django.id,
                                'form-INITIAL_FORMS':0,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':3})
        self.assertEqual(res.status_code, 302) # redirect after POST
        topic_id = res['location'].split('/')[-2] # id of the new topic
        t = Topic.objects.get(pk=topic_id)
        self.assertEqual(t.title, 'test topic title')
        self.assertEqual(t.description, 'test topic description')
        self.assertEqual(Topic.objects.count(), 3) # make sure we created
                                                   # a new topic
        # cleanup
        t.delete()

    def testListView (self):
        res = self.client.get(reverse('topic-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'committees/topic_list.html')
        self.assertQuerysetEqual(res.context['topics'],
                                 ["<Topic: hello>", "<Topic: bye>"])

    def testRanking(self):
        self.assertQuerysetEqual(Topic.objects.all(),
                                 ["<Topic: hello>", "<Topic: bye>"])
        self.topic2.rating.add(score=4, user=self.ofri, ip_address="127.0.0.1")
        self.assertQuerysetEqual(Topic.objects.by_rank(),
                                 ["<Topic: bye>", "<Topic: hello>"])

    def tearDown(self):
        self.django.delete()
        self.python.delete()
        self.jacob.delete()
        self.group.delete()
        self.topic.delete()
