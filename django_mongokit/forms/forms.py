import datetime
from django import forms
from django.utils import simplejson

from django.utils.datastructures import SortedDict
from django.forms.util import ValidationError, ErrorList
from django.forms.forms import BaseForm, get_declared_fields, NON_FIELD_ERRORS

from fields import JsonField, JsonListField

def save_instance(form, instance, fields=None, fail_message='saved',
                  commit=True, exclude=None):
    if form.errors:
        raise ValueError("The %s could not be %s because the data didn't"
                " validate." % ('object', fail_message))

    cleaned_data = form.cleaned_data

    for field_name, field_type in instance.structure.items():
        if fields and field_name not in fields:
            continue
        if exclude and field_name in exclude:
            continue

        instance[field_name] = cleaned_data[field_name]

    if commit:
        instance.save(validate=True)

    return instance

def get_field_type_from_document(instance, field_name):

    field_type = instance.structure[field_name]
    if isinstance(field_type, list):
        field_type = list
    if isinstance(field_type, dict):
        field_type = dict

    return field_type

def value_from_document(instance, field_name):

    field_type = get_field_type_from_document(instance, field_name)

    # Refactor this into a class for each data type.
    if field_type in [list, dict]:
        return simplejson.dumps(instance[field_name])

    return instance[field_name]

def document_to_dict(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    # avoid a circular import
    structure = instance.structure

    data = {}
    for field_name in structure.keys():
        if fields and not field_name in fields:
            continue
        if exclude and field_name in exclude:
            continue
        data[field_name] = value_from_document(instance, field_name)

    return data

def get_default_form_field_types(document, field_name, field_type):
    #if field_name in document.custom_fields:
    #    return document.custom_fields[field_name]
    #else:
    default_form_field_types = {
            bool: forms.BooleanField,
            int: forms.IntegerField,
            float: forms.FloatField,
            str: forms.CharField,
            unicode: forms.CharField,
            datetime.datetime: forms.DateTimeField,
            datetime.date: forms.DateField,
            datetime.time: forms.TimeField,
            list: JsonListField,
            dict: JsonField,
    }
    return default_form_field_types[field_type]

def formfield_for_document_field(document, field_name,
        form_class=forms.CharField, **kwargs):

    field_type = get_field_type_from_document(document, field_name)
    FormField = get_default_form_field_types(document,field_name,field_type)

    defaults = {
        'required': field_name in document.required_fields,
    }
    if field_type == list:
        defaults['initial'] = '[]'
    if field_type == dict:
        defaults['initial'] = '{}'

    if field_name in document.default_values:
        default_value = document.default_values[field_name]
        if callable(default_value):
            default_value = default_value()
        defaults['initial'] = default_value
    #if field_name in document.label_values:
    #    label_value = document.label_values[field_name]
    #    defaults['label'] = label_value

    defaults.update(kwargs)
    formfield = FormField(**defaults)
    return formfield

def fields_for_document(document, fields=None, exclude=None,
        formfield_callback=None):
    """
    Returns a ``SortedDict`` containing form fields for the given model.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned fields.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned fields, even if they are listed
    in the ``fields`` argument.
    """
    field_list = []
    structure = document.structure
    for field_name, field_type in structure.items():
        if fields and not field_name in fields:
            continue
        if exclude and field_name in exclude:
            continue

        form_field = None
        if formfield_callback:
            form_field = formfield_callback(document, field_name)
        if not form_field:
            form_field = formfield_for_document_field(document, field_name)
        if form_field:
            field_list.append((field_name, form_field))

    field_dict = SortedDict(field_list)
    if fields:
        field_dict = SortedDict([(f, field_dict.get(f))
                for f in fields
                if (not exclude) or (exclude and f not in exclude)])
    return field_dict

class DocumentFormOptions(object):
    def __init__(self, options=None):

        try:
            self.document = getattr(options, 'document')
        except AttributeError:
            raise AttributeError("DocumentForm must specify a document class.")

        try:
            self.document.collection
        except AttributeError:
            pass
        else:
            raise TypeError("Document must not be bound to a collection.")

        self.fields = getattr(options, 'fields', None)
        self.exclude = getattr(options, 'exclude', None)

class DocumentFormMetaclass(type):
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.pop('formfield_callback', None)
        try:
            parents = [b for b in bases if issubclass(b, DocumentForm)]
        except NameError:
            # We are defining ModelForm itself.
            parents = None
        declared_fields = get_declared_fields(bases, attrs, False)
        new_class = super(DocumentFormMetaclass, cls).__new__(cls, name, bases,
                attrs)
        if not parents:
            return new_class

        opts = new_class._meta = DocumentFormOptions(getattr(new_class, 'Meta', None))
        if opts.document:
            # If a model is defined, extract form fields from it.
            fields = fields_for_document(opts.document, opts.fields,
                                      opts.exclude, formfield_callback)
            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(declared_fields)
        else:
            fields = declared_fields
        new_class.declared_fields = declared_fields
        new_class.base_fields = fields
        return new_class

class BaseDocumentForm(BaseForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None,
                 collection=None):

        opts = self._meta
        if instance is None:
            # if we didn't get an instance, instantiate a new one
            if collection is None:
                raise TypeError("Collection must be supplied for an unbound "
                        "DocumentForm")
            self.instance = opts.document(collection=collection)
            object_data = {}
        else:
            self.instance = instance
            try:
                self.instance.collection
            except AttributeError:
                raise AssertionError("Instance must be bound to a collection.")

            object_data = document_to_dict(instance, opts.fields, opts.exclude)
        # if initial was provided, it should override the values from instance
        if initial is not None:
            object_data.update(initial)
        super(BaseDocumentForm, self).__init__(data, files, auto_id, prefix, object_data,
                                            error_class, label_suffix, empty_permitted)

    def save(self, commit=True):
        if self.instance.get('_id', None) is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'
        return save_instance(self, self.instance, self._meta.fields,
                             fail_message, commit, exclude=self._meta.exclude)

    save.alters_data = True

class DocumentForm(BaseDocumentForm):
    __metaclass__ = DocumentFormMetaclass


def documentform_factory(document, form=DocumentForm,
        fields=None, exclude=None,
        formfield_callback=None):
    # Create the inner Meta class. FIXME: ideally, we should be able to
    # construct a ModelForm without creating and passing in a temporary
    # inner class.

    # Build up a list of attributes that the Meta object will have.

    try:
        document.collection
    except AttributeError:
        pass
    else:
        raise TypeError("Document must not be bound.")

    attrs = { 'document': document }
    if fields is not None:
        attrs['fields'] = fields
    if exclude is not None:
        attrs['exclude'] = exclude

    # If parent form class already has an inner Meta, the Meta we're
    # creating needs to inherit from the parent's inner meta.
    parent = (object,)
    if hasattr(form, 'Meta'):
        parent = (form.Meta, object)
    Meta = type('Meta', parent, attrs)

    # Give this new form class a reasonable name.
    class_name = '%sForm' % document.__name__

    # Class attributes for the new form class.
    form_class_attrs = {
        'Meta': Meta,
        'formfield_callback': formfield_callback
    }

    return DocumentFormMetaclass(class_name, (form,), form_class_attrs)