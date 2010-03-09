import datetime
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Talk
from forms import TalkForm


def homepage(request):
    talks = Talk.objects.all().order_by('-when')
    if request.method == "POST":
        form = TalkForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['topic']
            w = form.cleaned_data['when']
            when = datetime.datetime(w.year, w.month, w.day, 0,0,0)
            tags = form.cleaned_data['tags']
            duration = form.cleaned_data['duration']
            talk = Talk.objects.create(topic=topic, when=when,
                                       tags=tags, duration=duration)
            
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = TalkForm()
            
    return render_to_response("exampleapp/home.html", locals(), 
                              context_instance=RequestContext(request))


def delete_talk(request, _id):
    Talk.objects.filter(pk=_id).delete()
    return HttpResponseRedirect(reverse("homepage"))