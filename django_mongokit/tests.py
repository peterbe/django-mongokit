import os
import unittest
from document import DjangoDocument

class Talk(DjangoDocument):
    structure = {'topic': unicode}
    
class CrazyOne(DjangoDocument):
    class Meta:
        verbose_name = u"Crazy One"
    structure = {'name': unicode}
        
class CrazyTwo(DjangoDocument):
    class Meta:
        verbose_name = u"Crazy Two"
        verbose_name_plural = u"Crazies Two"
    structure = {'names': unicode}
        
class LighteningTalk(Talk):
    structure = {'has_slides': bool}
    default_values = {'has_slides': True}
    
    
class DocumentTest(unittest.TestCase):
    
    def setUp(self):
        from shortcut import connection
        connection.register([Talk, CrazyOne, CrazyTwo, LighteningTalk])
        
        self.connection = connection
        self.database = connection['django_mongokit_test_database']
        
    def tearDown(self):
        self.connection.drop_database('django_mongokit_test_database')
    
    def test_meta_creation(self):
        """the class Talk define above should have been given an attribute 
        '_meta' by the metaclass that registers it"""
        klass = Talk
        self.assertTrue(klass._meta)
        self.assertFalse(hasattr(klass._meta, 'abstract'))
        self.assertEqual(klass._meta.verbose_name, u"Talk")
        self.assertEqual(klass._meta.verbose_name_plural, u"Talks")
        self.assertEqual(klass._meta.app_label, u"__main__") # test runner
        self.assertEqual(klass._meta.model_name, u"Talk")
        
        self.assertEqual(klass._meta.pk.attname, '_id')
        
        repr_ = repr(klass._meta)
        # <Meta Talk: 'Talk', 'Talks'>
        self.assertEqual(repr_.count('Talk'), 3)
        self.assertEqual(repr_.count('Talks'), 1)
        
    def test_meta_creation_overwriting_verbose_name(self):
        klass = CrazyOne
        self.assertTrue(klass._meta)
        self.assertEqual(klass._meta.verbose_name, u"Crazy One")
        self.assertEqual(klass._meta.verbose_name_plural, u"Crazy Ones")
        self.assertEqual(klass._meta.model_name, u"CrazyOne")
        
    def test_meta_creation_overwriting_verbose_name_and_plural(self):
        klass = CrazyTwo
        self.assertTrue(klass._meta)
        self.assertEqual(klass._meta.verbose_name, u"Crazy Two")
        self.assertEqual(klass._meta.verbose_name_plural, u"Crazies Two")
        self.assertEqual(klass._meta.model_name, u"CrazyTwo")
        
    def test_subclassed_document(self):
        klass = LighteningTalk
        self.assertTrue(klass._meta)
        self.assertEqual(klass._meta.verbose_name, u"Lightening Talk")
        self.assertEqual(klass._meta.verbose_name_plural, u"Lightening Talks")
        self.assertEqual(klass._meta.model_name, u"LighteningTalk")
        
    def test_pk_shortcut(self):
        # create an instance an expect to get the ID as a string
        collection = self.database.talks
        talk = collection.Talk()
        self.assertRaises(KeyError, lambda t:t.pk, talk)
        talk['topic'] = u"Something"
        talk.save()
        self.assertTrue(talk['_id'])
        self.assertTrue(talk.pk)
        self.assertTrue(isinstance(talk.pk, str))
        self.assertEqual(talk.pk, str(talk['_id']))
        
        def setter(inst, forced_id):
            inst.pk = forced_id # will fail
        self.assertRaises(ValueError, setter, talk, 'bla')
        
    def test_signals(self):
        #self.connection.register([LighteningTalk])
        
        _fired = []
        
        def trigger_pre_delete(sender, instance, **__):
            if sender is LighteningTalk:
                if isinstance(instance, LighteningTalk):
                    _fired.append('pre_delete')

        def trigger_post_delete(sender, instance, **__):
            if sender is LighteningTalk:
                if isinstance(instance, LighteningTalk):
                    _fired.append('post_delete')
                    
        def trigger_pre_save(sender, instance, raw=None, **__):
            if sender is LighteningTalk:
                if isinstance(instance, LighteningTalk):
                    if not getattr(instance, '_id', None):
                        _fired.append('pre_save')


        def trigger_post_save(sender, instance, raw=None, created=False, **__):
            assert created in (True, False), "created is supposed to be a bool"
            if sender is LighteningTalk:
                if isinstance(instance, LighteningTalk):
                    if created:
                        _fired.append('post_save created')
                    else:
                        _fired.append('post_save not created')
                    if '_id' in instance:
                        _fired.append('post_save')

        from django.db.models import signals
        signals.pre_delete.connect(trigger_pre_delete, sender=LighteningTalk)
        signals.post_delete.connect(trigger_post_delete, sender=LighteningTalk)

        signals.pre_save.connect(trigger_pre_save, sender=LighteningTalk)
        signals.post_save.connect(trigger_post_save, sender=LighteningTalk)

        collection = self.database.talks
        talk = collection.LighteningTalk()
        
        talk['topic'] = u"Bla"
        talk.save()
        
        self.assertTrue('pre_save' in _fired)
        self.assertTrue('post_save' in _fired)
        self.assertTrue('post_save created' in _fired)
        self.assertTrue('post_save not created' not in _fired)
        
        talk.delete()
        self.assertTrue('pre_delete' in _fired)
        self.assertTrue('post_delete' in _fired)
        
        talk['topic'] = u"Different"
        talk.save()
        self.assertTrue('post_save not created' in _fired)
        
        
class ShortcutTestCase(unittest.TestCase):
    
    def test_get_database(self):
        from shortcut import get_database, connection
        db = get_database()
        self.assertEqual(db.connection, connection)

        db = get_database(connection)
        self.assertEqual(db.connection, connection)
        
    def test_get_version(self):
        from shortcut import get_version
        version = get_version()
        self.assertEqual(version,
                         open(os.path.join(os.path.dirname(__file__), 
                         'version.txt')).read())


class MongoDBBaseTestCase(unittest.TestCase):
    
    def test_load_backend(self):
        from django.db import connections
        self.assertTrue('mongodb' in connections)

        from django.db.utils import load_backend
        backend = load_backend('django_mongokit.mongodb')
        self.assertTrue(backend is not None)
        
    def test_database_wrapper(self):
        from django.db import connections
        connection = connections['mongodb']
        self.assertTrue(hasattr(connection, 'connection')) # stupid name!
        # needed attribute
        self.assertTrue(hasattr(connection.connection, 'autocommit'))
        
    def test_create_test_database(self):
        from django.conf import settings
        assert 'mongodb' in settings.DATABASES
        old_database_name = settings.DATABASES['mongodb']['NAME']
        assert 'test_' not in old_database_name
        # pretend we're the Django 'test' command
        
        from django.db import connections
        connection = connections['mongodb']
        
        connection.creation.create_test_db()
        test_database_name = settings.DATABASES['mongodb']['NAME']
        self.assertTrue('test_' in test_database_name)
        
        from mongokit import Connection
        con = Connection()
        # the test database isn't created till it's needed
        self.assertTrue(test_database_name not in con.database_names())
        
        # creates it
        db = con[settings.DATABASES['mongodb']['NAME']]
        coll = db.test_collection_name
        # do a query on the collection to force the database to be created
        list(coll.find())
        test_database_name = settings.DATABASES['mongodb']['NAME']
        self.assertTrue(test_database_name in con.database_names())
        
        connection.creation.destroy_test_db(old_database_name)
        self.assertTrue('test_' not in settings.DATABASES['mongodb']['NAME'])
        self.assertTrue(test_database_name not in con.database_names())
        
        # this should work even though it doesn't need to do anything
        connection.close()
        
    def test_create_test_database_by_specific_bad_name(self):
        from django.conf import settings
        assert 'mongodb' in settings.DATABASES
        settings.DATABASES['mongodb']['TEST_NAME'] = "muststartwith__test_"
        old_database_name = settings.DATABASES['mongodb']['NAME']
        from django.db import connections
        connection = connections['mongodb']
        
        # why doesn't this work?!?!
        #from mongodb.base import DatabaseError
        #self.assertRaises(DatabaseError, connection.creation.create_test_db)
        self.assertRaises(Exception, connection.creation.create_test_db)
        
        
    def test_create_test_database_by_specific_good_name(self):
        from django.conf import settings
        assert 'mongodb' in settings.DATABASES
        settings.DATABASES['mongodb']['TEST_NAME'] = "test_mustard"
        old_database_name = settings.DATABASES['mongodb']['NAME']
        from django.db import connections
        connection = connections['mongodb']
        
        connection.creation.create_test_db()
        test_database_name = settings.DATABASES['mongodb']['NAME']
        self.assertTrue('test_' in test_database_name)
        
        from mongokit import Connection
        con = Connection()
        # the test database isn't created till it's needed
        self.assertTrue(test_database_name not in con.database_names())
        
        # creates it
        db = con[settings.DATABASES['mongodb']['NAME']]
        coll = db.test_collection_name
        # do a query on the collection to force the database to be created
        list(coll.find())
        test_database_name = settings.DATABASES['mongodb']['NAME']
        self.assertTrue(test_database_name in con.database_names())
        
        connection.creation.destroy_test_db(old_database_name)
        self.assertTrue('test_mustard' not in settings.DATABASES['mongodb']['NAME'])
        self.assertTrue(test_database_name not in con.database_names())
        
if __name__ == '__main__':
    unittest.main()
