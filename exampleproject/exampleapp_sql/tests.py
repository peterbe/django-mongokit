from django.core.urlresolvers import reverse
import datetime
from django.test import TestCase
from django.db import connections
from django.conf import settings

from models import Talk

class ExampleTest(TestCase):
    def setUp(self):
        self.connection = connections['mongodb'].connection
        self.database = self.connection[settings.DATABASES['mongodb']['NAME']]
        
    def tearDown(self):
        for name in self.database.collection_names():
            if name not in ('system.indexes',):
                self.database.drop_collection(name)

        
    def test_creating_talk_basic(self):
        """test to create a Talk instance"""
        talk = Talk.objects.create(topic=u"Bla",
                                   when=datetime.datetime.now(),
                                   tags=[u"foo", u"bar"],
                                   duration=5.5,
                                   )

        self.assertTrue(talk.id)
        self.assertEqual(talk.duration, 5.5)
        
    def test_homepage(self):
        """rendering the homepage will show talks and will make it possible to 
        add more talks and delete existing ones"""
        response = self.client.get(reverse('sql:homepage'))
        self.assertTrue(response.status_code, 200)
        self.assertTrue('No talks added yet' in response.content)
        
        data = {'topic': '', 
                'when': '2010-12-31',
                'duration':'1.0',
                'tags': ' foo , bar, ,'}
        response = self.client.post(reverse('sql:homepage'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('class="errorlist"' in response.content)
        self.assertTrue('This field is required' in response.content)
        
        data['topic'] = 'My Topic'
        response = self.client.post(reverse('sql:homepage'), data)
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('sql:homepage'))
        self.assertTrue(response.status_code, 200)
        self.assertTrue('My Topic' in response.content)
        self.assertTrue('31 December 2010' in response.content)
        self.assertTrue('Tags: foo, bar' in response.content)
        
        talk = Talk.objects.all()[0]
        assert talk.topic == u"My Topic"
        delete_url = reverse('sql:delete_talk', args=[talk.pk])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('sql:homepage'))
        self.assertTrue(response.status_code, 200)
        self.assertTrue('My Topic' not in response.content)
        
        
        
        
        
