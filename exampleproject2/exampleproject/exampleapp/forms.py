import datetime

from django import forms

from django_mongokit.forms import DocumentForm
from models import Talk

class TalkForm(DocumentForm):
    
    tags = forms.CharField(max_length=250)
    
    def clean_tags(self):
        value = self.cleaned_data['tags']
        return [tag.strip() for tag in value.split(',')]
    
    def clean_when(self):
        w = self.cleaned_data['when']
        when = datetime.datetime(w.year, w.month, w.day, 0,0,0)
        return when
    
    class Meta:
        document = Talk
        fields = ['topic', 'when', 'tags', 'duration']

