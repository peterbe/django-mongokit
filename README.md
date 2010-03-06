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
                'ENGINE': 'sqlite3', 
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