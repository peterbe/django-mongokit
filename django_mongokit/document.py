import sys
import re
from mongokit.document import DocumentProperties
try:
    from mongokit.connection import CallableMixin
except ImportError:
    # mongokit < 0.6
    from mongokit.document import CallableMixin
from mongokit import Document
from django.db.models import signals
model_names = []

from shortcut import connection

class _PK(object):
    attname = '_id'

class _Meta(object):
    def __init__(self, model_name, verbose_name, verbose_name_plural,
                 module_name=None,
                 app_label=None,
                 ):
        self.model_name = model_name
        self.verbose_name = verbose_name and verbose_name or \
          re.sub('([a-z])([A-Z])', r'\1 \2', model_name)
        self.verbose_name_plural = verbose_name_plural or self.verbose_name + 's'
        self.module_name = module_name
        self.app_label = app_label
        self.pk = _PK() # needed for haystack

        #all_verbose_names.append(verbose_name)
        model_names.append((model_name, self.verbose_name))

    def __repr__(self):
        return "<Meta %s %r, %r>" % (self.model_name,
                                     self.verbose_name,
                                     self.verbose_name_plural)


class DjangoDocumentMetaClass(DocumentProperties):
    def __new__(cls, name, bases, attrs):
        new_class = super(DjangoDocumentMetaClass, cls).__new__(cls, name, bases, attrs)

        if CallableMixin in bases:
            # When you register models in the views for example it will register
            # all the models again but then they'll be subclasses of mongokit's
            # CallableMixin.
            # When this is the case we don't want to bother registering any
            # meta stuff about them so exit here
            return new_class

        meta = attrs.pop('Meta', None)

        if meta and getattr(meta, 'abstract', False):
            # No need to attach more meta crap
            return new_class

        verbose_name = meta and getattr(meta, 'verbose_name', None) or None
        verbose_name_plural = meta and getattr(meta, 'verbose_name_plural', None) or None
        meta = _Meta(name, verbose_name, verbose_name_plural)

        model_module = sys.modules[new_class.__module__]
        try:
            meta.app_label = model_module.__name__.split('.')[-2]
        except IndexError:
            meta.app_label = model_module.__name__

        new_class._meta = meta
        return new_class


class DjangoDocument(Document):
    class Meta:
        abstract = True

    __metaclass__ = DjangoDocumentMetaClass

    ## XX Are these needed?
    def _get_pk_val(self, meta=None):
        if not meta:
            meta = self._meta
        #return str(getattr(self, meta.pk.attname))
        return str(self[meta.pk.attname])
    def _set_pk_val(self, value):
        raise ValueError("You can't set the ObjectId")
    pk = property(_get_pk_val, _set_pk_val)
    ##


    def delete(self):
        signals.pre_delete.send(sender=self.__class__, instance=self)
        super(DjangoDocument, self).delete()
        signals.post_delete.send(sender=self.__class__, instance=self)

    def save(self, *args, **kwargs):
        signals.pre_save.send(sender=self.__class__, instance=self)

        _id_before = '_id' in self and self['_id'] or None
        super(DjangoDocument, self).save(*args, **kwargs)
        _id_after = '_id' in self and self['_id'] or None

        signals.post_save.send(sender=self.__class__, instance=self,
                               created=bool(not _id_before and _id_after))
