
from django.forms.fields import CharField, ValidationError
from django.forms.widgets import TextInput, Textarea

try:
    import json as simplejson
except ImportError, e:
    if e.args[0].startswith('No module named json'):
        from django.utils import simplejson
    else:
        raise


class JsonField(CharField):

    widget = Textarea

    def to_python(self, value):
        """
        Validates that the input can be converted to a datetime. Returns a
        Python datetime.datetime object.
        """
        if not value:
            return {}

        try:
            return simplejson.loads(value)
        except ValueError, e:
            raise ValidationError(str(e))


class JsonListField(CharField):

    widget = TextInput

    def to_python(self, value):
        """
        Validates that the input can be converted to a datetime. Returns a
        Python datetime.datetime object.
        """
        if not value:
            return []

        try:
            return simplejson.loads(value)
        except ValueError, e:
            raise ValidationError(str(e))
