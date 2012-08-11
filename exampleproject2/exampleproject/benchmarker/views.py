#-*- coding: iso-8859-1 -*

import datetime
import random
from cStringIO import StringIO
from time import time, sleep
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import utc

from exampleproject.exampleapp.models import Talk
from exampleproject.exampleapp_sql.models import Talk as sql_Talk

from django_mongokit import get_database

def run(request):
    how_many = int(request.GET.get('how_many', 1))

    TESTS = (('mongokit', _create_talks, _edit_talks, _delete_talks,
              settings.DATABASES['mongodb']['ENGINE']),
             ('sql', _create_talks_sql, _edit_talks_sql, _delete_talks_sql,
              settings.DATABASES['default']['ENGINE']),
             )

    response = StringIO()

    for label, creator, editor, deletor, engine in TESTS:
        total = 0.0
        print >>response, label, engine

        t0=time()
        ids = creator(how_many)
        t1=time()
        total += t1-t0
        print >>response, "Creating", how_many, "talks took", t1-t0, "seconds"

        # give it a rest so that the database can internall index all the IDs
        sleep(1)

        t0=time()
        editor(ids)
        t1=time()
        total += t1-t0
        print >>response, "Editing", how_many, "talks took", t1-t0, "seconds"

        # give it a rest so that the database can internall index all the IDs
        sleep(1)

        t0=time()
        deletor(ids)
        t1=time()
        total += t1-t0
        print >>response, "Deleting", how_many, "talks took", t1-t0, "seconds"


        print >>response, "IN TOTAL", total, "seconds"
        print >>response, "\n"

    return HttpResponse(response.getvalue(), mimetype='text/plain')

def __random_topic():
    return random.choice(
        (u'No talks added yet',
         u"I'm working on a branch of django-mongokit that I thought you'd like to know about.",
         u'I want to learn Gaelic.',
         u"I'm well, thank you.",
         u' (Kaw uhn KEU-ra shin KAW-la root uh CHOO-nik mee uhn-royer?)',
         u'Chah beh shin KEU-ra, sheh shin moe CHYEH-luh uh vah EEN-tchuh!',
         u'STUH LUH-oom BRISS-kaht-chun goo MAWR',
         u"Suas Leis a' Ghàidhlig! Up with Gaelic!",
         u"Tha mi ag iarraidh briosgaid!",
        ))

def __random_when():
    return datetime.datetime(random.randint(2000, 2010),
                             random.randint(1, 12),
                             random.randint(1, 28),
                             0, 0, 0).replace(tzinfo=utc)

def __random_tags():
    tags = [u'one', u'two', u'three', u'four', u'five', u'six',
            u'seven', u'eight', u'nine', u'ten']
    random.shuffle(tags)
    return tags[:random.randint(0, 3)]

def __random_duration():
    return round(random.random()*10, 1)


def _create_talks(how_many):
    # 1 Create 1,000 talks
    collection = get_database()[Talk.collection_name]
    ids = set()
    for i in range(how_many):
        talk = collection.Talk()
        talk.topic = __random_topic()
        talk.when = __random_when()
        talk.tags = __random_tags()
        talk.duration = __random_duration()
        talk.save()
        ids.add(talk.pk)
    return ids

def _edit_talks(ids):
    collection = get_database()[Talk.collection_name]
    for id_ in ids:
        talk = collection.Talk.one({'_id': ObjectId(id_)})
        talk.topic += "extra"
        talk.save()

def _delete_talks(ids):
    collection = get_database()[Talk.collection_name]
    for id_ in ids:
        talk = collection.Talk.one({'_id': ObjectId(id_)})
        talk.delete()



def _create_talks_sql(how_many):
    # 1 Create 1,000 talks
    ids = set()
    for i in range(how_many):
        topic = __random_topic()
        when = __random_when()
        tags = __random_tags()
        duration = __random_duration()
        talk = sql_Talk.objects.create(topic=topic, when=when, tags=tags, duration=duration)
        ids.add(talk.pk)
    return ids

def _delete_talks_sql(ids):
    for id_ in ids:
        talk = sql_Talk.objects.get(pk=id_)
        talk.delete()

def _edit_talks_sql(ids):
    for id_ in ids:
        talk = sql_Talk.objects.get(pk=id_)
        talk.topic += "extra"
        talk.save()
