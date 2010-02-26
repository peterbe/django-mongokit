import datetime
from pymongo.objectid import ObjectId
from mongokit import Connection
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Talk
from forms import TalkForm

#DB_NAME = settings.DATABASES['mongodb']['NAME']
#con = Connection()
#con.register([Talk])
from django.db import connections

connection = connections['mongodb'].connection
database = connection[settings.DATABASES['mongodb']['NAME']]


def homepage(request):
    connection.register([Talk])
    collection = database[Talk.collection_name]
    talks = collection.Talk.find()
    talks.sort('when', -1)
    if request.method == "POST":
        form = TalkForm(request.POST)
        if form.is_valid():
            talk = collection.Talk()
            talk.topic = form.cleaned_data['topic']
            w = form.cleaned_data['when']
            talk.when = datetime.datetime(w.year, w.month, w.day, 0,0,0)
            talk.tags = form.cleaned_data['tags']
            talk.duration = form.cleaned_data['duration']
            talk.save()
            
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = TalkForm()
            
    return render_to_response("exampleapp/home.html", locals(), 
                              context_instance=RequestContext(request))


def delete_talk(request, _id):
    connection.register([Talk])
    collection = database[Talk.collection_name]
    talk = collection.Talk.one({"_id": ObjectId(_id)})
    talk.delete()
    return HttpResponseRedirect(reverse("homepage"))