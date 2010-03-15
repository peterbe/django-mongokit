from django.conf import settings
try:
    from django.db import connections
    from django.db.utils import ConnectionDoesNotExist

    __django_12__ = True
except ImportError:
    __django_12__ = False


if __django_12__:    
    try:
        connection = connections['mongodb'].connection
    except ConnectionDoesNotExist:
        # Need to raise a better error
        print connections.databases
        raise
else:
    # because this is Django <1.2 doesn't load all the engines so we have to 
    # do it manually. 
    # Since with Django <1.2 we have to first define a normal backend engine
    # like sqlite so then the base backend for mongodb is never called
    from django.db import load_backend
    backend = load_backend('django_mongokit.mongodb')
    connection = backend.DatabaseWrapper({
        'DATABASE_HOST': getattr(settings, 'MONGO_DATABASE_HOST', None),
        'DATABASE_NAME': settings.MONGO_DATABASE_NAME,
        'DATABASE_OPTIONS': getattr(settings, 'MONGO_DATABASE_OPTIONS', None),
        'DATABASE_PASSWORD': getattr(settings, 'MONGO_DATABASE_PASSWORD', None),
        'DATABASE_PORT': getattr(settings, 'MONGO_DATABASE_PORT', None),
        'DATABASE_USER': getattr(settings, 'MONGO_DATABASE_USER', None),
        'TIME_ZONE': settings.TIME_ZONE,
    })
    connection = connection.connection
    

# The reason this is a function rather than an instance is that you're supposed
# to get the database object every time by calling this function. If you define
# it as a instance (as we do with the connection) the database name cannot be
# different once everything has been imported and loaded.
# When you run tests Django will set everything up so that a test database is
# prepared and that changes settings.DATABASES automatically.
# The net effect is that the way the tests are run nothing needs to be done 
# differently as long as you use get_database()
def get_database(this_connection=connection):
    if __django_12__:
        return this_connection[settings.DATABASES['mongodb']['NAME']]
    else:
        return this_connection[settings.MONGO_DATABASE_NAME]


def get_version():
    import os
    f = os.path.join(os.path.dirname(__file__), 'version.txt')
    return open(f).read()