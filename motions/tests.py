from django.test import TestCase
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User,Group,Permission
from django.core.urlresolvers import reverse

from links.models import LinkType

from models import Motion, MOTION_REJECTED

class DriverModel(models.Model):
    name = models.TextField()
    motions = models.ManyToManyField('motions.Motion', blank=True)

class MotionsTest(TestCase):

    def setUp(self):
        self.django = DriverModel.objects.create(name='django')
        self.python = DriverModel.objects.create(name='python')
        self.jacob = User.objects.create_user('jacob', 'jacob@example.com',
                                              'JKM')
        self.ofri = User.objects.create_user('ofri', 'ofri@example.com',
                                              'ofri')
        (self.group, created) = Group.objects.get_or_create(name='Valid Email')
        self.jacob.groups.add(self.group)
        self.motion = self.django.motions.create(creator=self.jacob,
                                                title="hello", description="hello world")
        self.motion2 = self.django.motions.create(creator=self.ofri,
                                                title="bye", description="goodbye")
        self.linktype = LinkType.objects.create(title='default')

    def testBasic(self):
        self.assertEqual(self.django.motions.get_public().count(), 2)
        # reject a motion
        self.motion.set_status(MOTION_REJECTED, "just because")
        self.assertEqual(self.django.motions.get_public().count(), 1)
        self.assertEqual(Motion.objects.get_public().count(), 1)
        self.motion2.set_status(MOTION_REJECTED, "because I feel like it")
        self.assertEqual(self.django.motions.get_public().count(), 0)

    def testPermissions(self):
        self.assertTrue(self.motion.can_edit(self.jacob))
        self.assertFalse(self.motion.can_edit(self.ofri))
        self.motion.editors.add(self.ofri)
        self.assertTrue(self.motion.can_edit(self.ofri))
        self.motion.editors.remove(self.ofri)
        self.assertFalse(self.motion.can_edit(self.ofri))
        self.ofri.is_superuser = True
        self.ofri.save()
        self.assertTrue(self.motion.can_edit(self.ofri))
        self.ofri.is_superuser = False
        self.ofri.save()

    def test_edit_motion_logged_required(self):
        res = self.client.get(reverse('edit-motion',
                                 kwargs={'pk': self.motion.id}))
        self.assertEqual(res.status_code, 302) # login required
        self.assertTrue(self.client.login(username='ofri',
                                          password='ofri'))
        res = self.client.get(reverse('edit-motion',
                                 kwargs={'pk': self.motion.id}))
        self.assertEqual(res.status_code, 403) # user is not an editor
        self.assertTrue(self.client.login(username='jacob',
                                          password='JKM'))
        res = self.client.get(reverse('edit-motion',
                                 kwargs={'pk': self.motion.id}))
        self.assertEqual(res.status_code, 200) # user is an editor
        self.assertTemplateUsed(res, 'motions/edit_motion.html')

    def test_edit_motion_form(self):
        res = self.client.post(reverse('edit-motion',
                                 kwargs={'pk': self.motion.id}),
                               {'title':'test motion title',
                                'description': 'test motion description',
                                'form-INITIAL_FORMS':0,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':3})
        self.assertEqual(res.status_code, 302) # redirect to login
        self.assertTrue(res['location'].startswith('%s%s'  %
                                       ('http://testserver', settings.LOGIN_URL)))

    def test_edit_motion(self):
        self.assertTrue(self.client.login(username='jacob',
                                          password='JKM'))
        res = self.client.post(reverse('edit-motion',
                                 kwargs={'pk': self.motion.id}),
                               {'title':'test motion title',
                                'description': 'test motion description',
                                'form-INITIAL_FORMS':0,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':3})
        self.assertEqual(res.status_code, 302) # redirect after POST
        motion = Motion.objects.get(pk=self.motion.id)
        self.assertEqual(motion.title, 'test motion title')
        self.assertEqual(motion.description, 'test motion description')
        self.assertEqual(Motion.objects.count(), 2) # make sure we didn't create
                                                   # a new motion

    def test_add_motion(self):
        self.assertTrue(self.client.login(username='jacob',
                                          password='JKM'))
        res = self.client.post(reverse('add-motion'),
                               {'title':'test motion title',
                                'description': 'test motion description',
                                'committees':self.django.id,
                                'form-INITIAL_FORMS':0,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':3})
        self.assertEqual(res.status_code, 302) # redirect after POST
        motion_id = res['location'].split('/')[-2] # id of the new motion
        motion = Motion.objects.get(pk=motion_id)
        self.assertEqual(motion.title, 'test motion title')
        self.assertEqual(motion.description, 'test motion description')
        self.assertEqual(Motion.objects.count(), 3) # make sure we created
                                                   # a new motion
        # cleanup
        motion.delete()

    def testListView (self):
        res = self.client.get(reverse('motion-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'motions/motion_list.html')
        self.assertQuerysetEqual(res.context['motions'],
                                 ["<Motion: hello>", "<Motion: bye>"])

    def testRanking(self):
        self.assertQuerysetEqual(Motion.objects.all(),
                                 ["<Motion: hello>", "<Motion: bye>"])
        self.motion2.rating.add(score=4, user=self.ofri, ip_address="127.0.0.1")
        self.assertQuerysetEqual(Motion.objects.by_rank(),
                                 ["<Motion: bye>", "<Motion: hello>"])

    def tearDown(self):
        self.django.delete()
        self.python.delete()
        self.jacob.delete()
        self.group.delete()
        self.motion.delete()
