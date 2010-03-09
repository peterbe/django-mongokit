from django import forms

class TalkForm(forms.Form):
    topic = forms.CharField(max_length=250)
    when = forms.DateField()
    tags = forms.CharField(max_length=250)
    duration = forms.FloatField()
    
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        return [x.strip() for x in tags.split(',') if x.strip()]