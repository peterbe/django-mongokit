import datetime
from pymongo.objectid import ObjectId
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from django_mongokit import get_database, connection


from models import Talk
from forms import TalkForm

def homepage(request):

    collection = get_database()[Talk.collection_name]
    talks = collection.Talk.find()
    talks.sort('when', -1)
    talks_count = talks.count()

    if request.method == "POST":
        form = TalkForm(request.POST, collection=collection)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = TalkForm(collection=collection)

    return render_to_response("exampleapp/home.html", locals(),
                              context_instance=RequestContext(request))


def delete_talk(request, _id):
    collection = get_database()[Talk.collection_name]
    talk = collection.Talk.one({"_id": ObjectId(_id)})
    talk.delete()
    return HttpResponseRedirect(reverse("homepage"))