import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import translation
from django.conf import settings

from agendas.models import Agenda, AgendaVote
from agendas.tests.base import AgendasSetup
from laws.models import Vote, VoteAction
from mks.models import Party, Member
from committees.models import Committee, CommitteeMeeting


just_id = lambda x: x.id

class SimpleTest(AgendasSetup, TestCase):

    def testAgendaList(self):
        translation.activate(settings.LANGUAGE_CODE)
        # test anonymous user
        res = self.client.get(reverse('agenda-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/agenda_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list),
                         [ self.agenda_1.id, self.agenda_2.id, ])

        # test logged in user 1
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.get(reverse('agenda-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/agenda_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list),
                         [ self.agenda_1.id, self.agenda_2.id, ])

        # test logged in user 2
        self.assertTrue(self.client.login(username='superman', password='CRP'))
        res = self.client.get(reverse('agenda-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/agenda_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list),
                         [ self.agenda_1.id, self.agenda_2.id, self.agenda_3.id])

        # test logged in as superuser
        self.assertTrue(self.client.login(username='john', password='LSD'))
        res = self.client.get(reverse('agenda-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/agenda_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list),
                         [self.agenda_1.id,
                              self.agenda_2.id,
                              self.agenda_3.id])

        translation.deactivate()

    def testAgendaDetail(self):

        # Access public agenda while not logged in
        res = self.client.get('%s?all_mks' % reverse('agenda-detail',
                                      kwargs={'pk': self.agenda_1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'agendas/agenda_detail.html')
        self.assertEqual(res.context['object'].id, self.agenda_1.id)
        self.assertEqual(res.context['object'].description, self.agenda_1.description)
        self.assertEqual(res.context['object'].public_owner_name, self.agenda_1.public_owner_name)
        self.assertEqual(list(res.context['object'].editors.all()), [self.user_1])
        self.assertEqual(len(res.context['all_mks_ids']), 2)

    def test_agenda_edit(self):
        # Try to edit agenda while not logged in
        res = self.client.get(reverse('agenda-detail-edit',
                                      kwargs={'pk': self.agenda_1.id}))
        self.assertRedirects(res, reverse('agenda-detail',
                                          kwargs={'pk':self.agenda_1.id}))

        # login as a user who's not the editor and try
        self.assertTrue(self.client.login(username='john',
                                          password='LSD'))
        res = self.client.get(reverse('agenda-detail-edit',
                                      kwargs={'pk': self.agenda_1.id}))
        self.assertRedirects(res, reverse('agenda-detail',
                                          kwargs={'pk':self.agenda_1.id}))

        # now login as the editor and try again
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.get(reverse('agenda-detail-edit',
                                      kwargs={'pk': self.agenda_1.id}))
        self.assertTemplateUsed(res,
                                'agendas/agenda_detail_edit.html')
        self.assertEqual(res.context['object'].id, self.agenda_1.id)
        self.assertEqual(res.context['object'].description, self.agenda_1.description)
        self.assertEqual(res.context['object'].public_owner_name, self.agenda_1.public_owner_name)
        self.assertEqual(list(res.context['object'].editors.all()), [self.user_1])

        # try to edit
        res = self.client.post(reverse('agenda-detail-edit',
                                       kwargs={'pk':self.agenda_1.id}),
                               {'name':'test1',
                                'public_owner_name':'test2',
                                'description': 'test3 description description' \
                                +'description'})
        self.assertEqual(res.status_code, 302)
        agenda = Agenda.objects.get(id=self.agenda_1.id)
        self.assertEqual(agenda.name, 'test1')

    def test_agenda_ascribe_meeting_not_logged_in(self):
        url = reverse('update-editors-agendas')
        res = self.client.post(url,
                               {'form-0-agenda_id':self.agenda_1.id,
                                'form-0-object_type':'committeemeeting',
                                'form-0-reasoning':'test reasoning',
                                'form-0-vote_id':self.meeting_1.id,
                                'form-0-weight':0.3,
                                'form-INITIAL_FORMS':1,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':1,
                               }
                              )
        self.assertRedirects(res, "%s?next=%s" % (settings.LOGIN_URL, url),
                             status_code=302)

    def test_agenda_ascribe_meeting_not_editor(self):
        self.assertTrue(self.client.login(username='john',
                                          password='LSD'))
        res = self.client.post(reverse('update-editors-agendas'),
                               {'form-0-agenda_id':self.agenda_1.id,
                                'form-0-object_type':'committeemeeting',
                                'form-0-reasoning':'test reasoning',
                                'form-0-vote_id':self.meeting_1.id,
                                'form-0-weight':0.3,
                                'form-INITIAL_FORMS':1,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':1,
                               }
                              )
        self.assertEqual(res.status_code, 403)


    def test_agenda_ascribe_meeting(self):
        self.assertTrue(self.client.login(username='jacob',
                                          password='JKM'))
        res = self.client.post(reverse('update-editors-agendas'),
                               {'form-0-agenda_id':self.agenda_1.id,
                                'form-0-object_type':'committeemeeting',
                                'form-0-reasoning':'test reasoning',
                                'form-0-vote_id':self.meeting_1.id,
                                'form-0-weight':0.3,
                                'form-INITIAL_FORMS':1,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':1,
                               }
                              )
        self.assertRedirects(res,
                             reverse('committee-meeting',
                                         kwargs={'pk':self.meeting_1.id}),
                             status_code=302)
        a = Agenda.objects.get(pk=self.agenda_1.id)
        self.assertEqual([am.meeting for am in a.agendameetings.all()],
                         [self.meeting_1])

    def test_agenda_ascribe_vote_not_logged_in(self):
        url = reverse('update-editors-agendas')
        res = self.client.post(url,
                               {'form-0-agenda_id':self.agenda_1.id,
                                'form-0-object_type':'vote',
                                'form-0-reasoning':'test reasoning',
                                'form-0-vote_id':self.vote_1.id,
                                'form-0-weight':1.0,
                                'form-INITIAL_FORMS':1,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':1,
                               }
                              )
        self.assertRedirects(res, "%s?next=%s" % (settings.LOGIN_URL, url),
                             status_code=302)

    def test_agenda_ascribe_vote_not_editor(self):
        self.assertTrue(self.client.login(username='john',
                                          password='LSD'))
        res = self.client.post(reverse('update-editors-agendas'),
                               {'form-0-agenda_id':self.agenda_1.id,
                                'form-0-object_type':'vote',
                                'form-0-reasoning':'test reasoning',
                                'form-0-vote_id':self.vote_1.id,
                                'form-0-weight':1.0,
                                'form-INITIAL_FORMS':1,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':1,
                               }
                              )
        self.assertEqual(res.status_code, 403)


    def test_agenda_ascribe_vote(self):
        self.assertTrue(self.client.login(username='jacob',
                                          password='JKM'))
        res = self.client.post(reverse('update-editors-agendas'),
                               {'form-0-agenda_id':self.agenda_1.id,
                                'form-0-object_type':'vote',
                                'form-0-reasoning':'test reasoning',
                                'form-0-vote_id':self.vote_1.id,
                                'form-0-weight':1.0,
                                'form-0-importance':0.3,
                                'form-INITIAL_FORMS':1,
                                'form-MAX_NUM_FORMS':'',
                                'form-TOTAL_FORMS':1,
                               }
                              )
        self.assertRedirects(res,
                             reverse('vote-detail',
                                         kwargs={'object_id':self.vote_1.id}),
                             status_code=302)
        av = AgendaVote.objects.get(agenda=self.agenda_1,
                                    vote=self.vote_1)
        self.assertEqual(av.score, 1.0)
        self.assertEqual(av.importance, 0.3)
        self.assertEqual(av.reasoning, 'test reasoning')

    def testAgendaMkDetail(self):
        res = self.client.get(reverse('mk-agenda-detail',
                                      kwargs={'pk': self.agenda_1.id,
                                              'member_id': self.mk_1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/mk_agenda_detail.html')
        self.assertEqual(int(res.context['score']), -33)
        self.assertEqual(len(res.context['related_votes']), 2)

    def testAgendaDetailOptCacheFail(self):
        res = self.client.get(reverse('agenda-detail',
                                      kwargs={'pk': self.agenda_1.id}))

        self.agenda_4 = Agenda.objects.create(name='agenda 4',
                                              description='a bloody good agenda 4',
                                              public_owner_name='Dr. Jacob',
                                              is_public=True)

        res2 = self.client.get(reverse('agenda-detail',
                                       kwargs={'pk': self.agenda_4.id}))

        self.assertEqual(res2.status_code, 200)

    def _validate_vote(self, vote):
        self.assertIn('id', vote, "Got vote with no id in agenda-todo")
        self.assertIn('url', vote, "Got vote with no url in agenda-todo")
        self.assertIn('title', vote, "Got vote with no title in agenda-todo")
        self.assertIn('score', vote, "Got vote with no importance in agenda-todo")



    def test_suggest_votes_for_new_agenda(self):
        new_agenda = Agenda.objects.create(name='new agenda',
                                           description='a brand new agenda',
                                           public_owner_name='Dr. Jekill',
                                           is_public=True)
        res = self.client.get('/api/v2/agenda-todo/%s/?format=json' % new_agenda.id)
        self.assertEqual(res.status_code, 200)
        todo = json.loads(res.content)

        def _validate_vote_list(list_key):         
            self.assertIn(list_key, todo, 'Got a todo with no votes for new agenda')
            votes = todo[list_key]
            self.assertGreater(len(votes), 1, 'Too little votes returned for new agenda')
            for vote in votes:
                self._validate_vote(vote)
            
            self.assertGreaterEqual(votes[0]['score'], votes[1]['score'], "votes returned out of importance order")

        _validate_vote_list('votes_by_controversy')
        _validate_vote_list('votes_by_agendas')

    def test_suggest_votes_for_existing_agenda(self):
        """
        We expect to get only self.vote_1 and self.vote_3 returned for agenda_2
        """
        res = self.client.get('/api/v2/agenda-todo/%s/?format=json' % self.agenda_2.id)
        self.assertEqual(res.status_code, 200)
        todo = json.loads(res.content)

        def _validate_vote_list(list_key):         
            self.assertIn(list_key, todo, 'Got a todo with no votes for new agenda')
            votes = todo[list_key]
            print votes
            self.assertEquals(len(votes), 2, 'Got wrong number of "votes" for existing agenda')
            vote = votes[0]
            self._validate_vote(vote)
            self.assertEqual(vote['id'], self.vote_1.id, "Expected vote not returned for existing agenda")

        _validate_vote_list('votes_by_controversy')
        _validate_vote_list('votes_by_agendas')
