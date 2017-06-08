"""
MongoKit (MongoDB) backend for Django.
"""

from mongokit import Connection

import django

if django.VERSION < (1, 8):
    from django.db.backends import (
        BaseDatabaseOperations,
        BaseDatabaseClient,
        BaseDatabaseIntrospection,
        BaseDatabaseWrapper,
        BaseDatabaseFeatures,
        BaseDatabaseValidation
    )
    from django.db.backends.creation import BaseDatabaseCreation
else:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.backends.base.client import BaseDatabaseClient
    from django.db.backends.base.features import BaseDatabaseFeatures
    from django.db.backends.base.validation import BaseDatabaseValidation
    from django.db.backends.base.introspection import BaseDatabaseIntrospection
    from django.db.backends.base.operations import BaseDatabaseOperations
    from django.db.backends.base.creation import BaseDatabaseCreation

from django.conf import settings

TEST_DATABASE_PREFIX = 'test_'


class UnsupportedConnectionOperation(Exception):
    pass


def complain(*args, **kwargs):
    raise UnsupportedConnectionOperation("ARGS=%s" % unicode(args))


def ignore(*args, **kwargs):
    pass


class DatabaseError(Exception):
    pass


class IntegrityError(DatabaseError):
    pass


class DatabaseOperations(BaseDatabaseOperations):

    def quote_name(self, name):
        return '<%s>' % name

    def sql_flush(self, *args, **kwargs):
        # deliberately do nothing as this doesn't apply to us
        return [True]  # pretend that we did something


class DatabaseClient(BaseDatabaseClient):
    runshell = complain


class DatabaseIntrospection(BaseDatabaseIntrospection):
    def get_table_list(self, cursor):
        return []
    get_table_description = complain
    get_relations = complain
    get_indexes = complain


class DatabaseCreation(BaseDatabaseCreation):
    def create_test_db(self, verbosity=1, autoclobber=False):
        # No need to create databases in mongoDB :)
        # but we can make sure that if the database existed is emptied

        if self.connection.settings_dict.get('TEST_NAME'):
            test_database_name = self.connection.settings_dict['TEST_NAME']
        elif 'NAME' in self.connection.settings_dict:
            test_database_name = (TEST_DATABASE_PREFIX +
                                  self.connection.settings_dict['NAME'])
        elif 'DATABASE_NAME' in self.connection.settings_dict:
            if (self.connection.settings_dict['DATABASE_NAME']
                .startswith(TEST_DATABASE_PREFIX)):
                # already been set up
                # must be because this is called from a setUp() instead of
                # something formal.
                # suspect this Django 1.1
                test_database_name = (self.connection
                                      .settings_dict['DATABASE_NAME'])
            else:
                test_database_name = TEST_DATABASE_PREFIX + \
                  self.connection.settings_dict['DATABASE_NAME']
        else:
            raise ValueError("Name for test database not defined")

        # This is important. Here we change the settings so that all other code
        # things that the chosen database is now the test database. This means
        # that nothing needs to change in the test code for working with
        # connections, databases and collections. It will appear the same as
        # when working with non-test code.
        try:
            settings.DATABASES['mongodb']['NAME'] = test_database_name
        except AttributeError:
            settings.MONGO_DATABASE_NAME = test_database_name

        settings.DATABASE_SUPPORTS_TRANSACTIONS = False  # MongoDB :)

        # In this phase it will only drop the database if it already existed
        # which could potentially happen if the test database was created but
        # was never dropped at the end of the tests
        self._drop_database(test_database_name)
        # if it didn't exist it will automatically be created by the
        # mongokit conncetion

    def destroy_test_db(self, old_database_name, verbosity=1):
        """
        Destroy a test database, prompting the user for confirmation if the
        database already exists. Returns the name of the test database created.
        """
        if verbosity >= 1:
            print "Destroying test database '%s'..." % self.connection.alias
        if 'DATABASE_NAME' in self.connection.settings_dict:
            # Django <1.2
            test_database_name = settings.MONGO_DATABASE_NAME
        else:
            test_database_name = self.connection.settings_dict['NAME']
        self._drop_database(test_database_name)

        try:
            settings.DATABASES['mongodb']['NAME'] = old_database_name
        except AttributeError:
            # Django <1.2
            settings.MONGO_DATABASE_NAME = old_database_name

    def _drop_database(self, database_name):
        if not database_name.startswith(TEST_DATABASE_PREFIX):
            # paranoia
            raise DatabaseError(
                "Suspicous! Can't delete database (%r) unless it's "
                "prefixed by %s" %
                (database_name, TEST_DATABASE_PREFIX)
            )
        if database_name in self.connection.connection.database_names():
            # needs to be dropped
            self.connection.connection.drop_database(database_name)


class DatabaseFeatures(BaseDatabaseFeatures):
    def __init__(self, connection):
        super(DatabaseFeatures, self).__init__(connection)

    @property
    def supports_transactions(self):
        return False

class DatabaseWrapper(BaseDatabaseWrapper):
    operators = {}
    _commit = ignore
    _rollback = ignore

    autocommit = None  # ignore

    # Django >= 1.11
    class DummyClass():
        def __init__(self, *args, **kwargs):
            pass

    client_class = DummyClass
    creation_class = DummyClass
    features_class = DummyClass
    introspection_class = DummyClass
    ops_class = DummyClass
    validation_class = DummyClass


    def __init__(self, settings_dict, alias=None, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(
            settings_dict,
            alias=alias,
            *args,
            **kwargs
        )

        if settings_dict['HOST']:
            kwargs['host'] = settings_dict['HOST']
        if settings_dict['PORT']:
            kwargs['port'] = int(settings_dict['PORT'])
        if 'OPTIONS' in settings_dict:
            kwargs.update(settings_dict['OPTIONS'])
        self.connection = ConnectionWrapper(**kwargs)

        try:
            self.features = DatabaseFeatures(self.connection)
        except TypeError:
            # Django < 1.3
            self.features = BaseDatabaseFeatures()

        try:
            self.ops = DatabaseOperations(self.connection)
        except TypeError:
            # Django < 1.4
            self.ops = DatabaseOperations()

        self.client = DatabaseClient(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        try:
            self.validation = BaseDatabaseValidation(self)
        except TypeError:
            # Django < 1.2
            self.validation = BaseDatabaseValidation()

        settings_dict['SUPPORTS_TRANSACTIONS'] = False
        self.settings_dict = settings_dict
        self.alias = alias and alias or settings_dict['DATABASE_NAME']

        # transaction related attributes
        self.transaction_state = None

    def close(self):
        pass


class ConnectionWrapper(Connection):
    # Need to pretend we care about autocommit
    # BaseDatabaseCreation (in django/db/backends/creation.py) needs to
    # set autocommit
    autocommit = True  # Needed attribute but its value is ignored

    def __init__(self, *args, **kwargs):
        super(ConnectionWrapper, self).__init__(*args, **kwargs)

    def __repr__(self):
        return ('ConnectionWrapper: ' +
                super(ConnectionWrapper, self).__repr__())
