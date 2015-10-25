# coding: utf-8

import json

from django.forms.fields import CharField, ValidationError
from django.forms.widgets import TextInput, Textarea


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
            return json.loads(value)
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
            return json.loads(value)
        except ValueError, e:
            raise ValidationError(str(e))
