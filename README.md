django-mongokit
===============

(c) Peter Bengtsson, peter@fry-it.com, 2010
License: New BSD License

Bridging Django to MongoDB with the MongoKit ODM
------------------------------------------------

The purpose of this module is to make it easy to use
[MongoKit](http://bitbucket.org/namlook/mongokit/wiki/Home) to
define your models for Django if you prefer to use MongoDB instead of
a relational database. This kit takes care of the boilerplate and
makes your MongoKit documents work better with Django as it defines a
`_meta` class attribute when registering.

Installation
------------

`pip/easy_install django-mongokit`

Usage/Configuration
-------------------

First of all you need to define a name of the database and but that
into your `settings.DATABASES` directive. Here's an example:

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'example-sqlite3.db',
            },
            'mongodb': {
                'ENGINE': 'django_mongokit.mongodb',
                'NAME': 'example',
            },
        }

Note that `default` and `mongodb` are mandatory keys in this settings.
What you can change is the `NAME` part under `DATABASES['mongodb']`.

In Django, you might be used to doing something like this:

        from django.db import models

        class Talk(models.Model):
	    topic = models.CharField(max_length=250)
	    date = models.DateTimeField()

Now, with `django_mongokit` you can do this:

        from django_mongokit.document import DjangoDocument

        class Talk(DjangoDocument):
	    structure = {
	       'topic': unicode,
	       'date': datetime.datetime
	    }

This base class gives you some benefits out-of-the-box which will
hopefully make working with MongoKit documents easier such as `pk`.
This will return the `ObjectID` of an instance as a byte string which
can be very useful for mapping URLs and finding documents by ID. For
example:

	>>> from mongokit import Connection
	>>> conn = Connection()
	>>> from exampleapp.models import Talk
	>>> conn.register([Talk])
	>>> database = conn['example']
	>>> collection = database['talks']
	>>> talk = collection.Talk.find_one()
	>>> talk
	'4b87c6b19d40b3375a000001'

There's also the `_meta` attribute which Django people will be
familiar with:

        >>> talk._meta
	<Meta Talk 'Talk', 'Talks'>
	>>> talk._meta.verbose_name
	'Talk'
	>>> talk._meta.verbose_name_plural
	'Talks'

If you want to override any of the `_meta` attributes you do it just
like you do it with the Django ORM:


        class Talk(models.Model):
	    ...
	    class Meta:
	        verbose_name_plural = u"Talkings"

A limited set of signals are fired when working with `django_mongokit`
documents. These are:

* pre_delete
* post_delete
* pre_save
* post_save


Examples
--------

`django-mongokit` comes with an example project and an example app
that does some basic things. It might be a good source of inspiration
for how to use `django-mongokit` to look at this example app.


Django 1.1 (pre multi-db support)
---------------------------------

`django-mongokit` was built for Django 1.2 with the multi-db support
but you can use `django-mongokit` in Django 1.1 (tested in Django
1.1.1) as a secondary database. For example, you might want to
continue running your application in MySQL/PosgreSQL/Oracle as it is
but you then have a fast logging app that writes to MongoDB. The way
difference from using Django 1.2 is to that you need to specify a
setting called `MONGO_DATABASE_NAME` like this:

        MONGO_DATABASE_NAME = "example"

Document Forms
--------------

A version of Django's ModelForm has been supplied for Mongokit Documents, called DocumentForm.

Using it is as simple as:

    from django_mongokit.forms import DocumentForm
    from models import Talk

    class TalkForm(DocumentForm):

        class Meta:
            document = Talk

This automatically pulls the fields from mongokit's `structure` attribute, along with associated `required_fields` and `default_values`, and builds associated form fields for this document.

You can customize the `DocumentForm` just like you'd customize a `ModelForm`:

    class TalkForm(DocumentForm):

        def clean_when(self):
            """
            Take a date object from the DateField and create a
            datetime object.
            """
            w = self.cleaned_data['when']
            when = datetime.datetime(w.year, w.month, w.day, 0,0,0)
            return when

        class Meta:
            document = Talk
            fields = ['topic', 'tags']
            # You could also explicitly exclude fields
            # exclude = ['created_on']

Right now, DocumentForms support the following mongokit datatypes: `int`, `bool`, `float`, `unicode`, `datetime.datetime`, `datetime.date`, `datetime.time`, `list` and `dict` (`list` and `dict` show up as character fields editable in JSON format). DocumentForms do not support nested documents or nested dictionary keys at the moment.

DocumentForms do not at the moment support mongokit validations.
