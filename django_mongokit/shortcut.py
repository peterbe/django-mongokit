from django.conf import settings
from django.db import connections

connection = connections['mongodb'].connection

# The reason this is a function rather than an instance is that you're supposed
# to get the database object every time by calling this function. If you define
# it as a instance (as we do with the connection) the database name cannot be
# different once everything has been imported and loaded.
# When you run tests Django will set everything up so that a test database is
# prepared and that changes settings.DATABASES automatically.
# The net effect is that the way the tests are run nothing needs to be done 
# differently as long as you use get_database()
def get_database(this_connection=connection):
    return connection[settings.DATABASES['mongodb']['NAME']]


def get_version():
    import os
    f = os.path.join(os.path.dirname(__file__), 'version.txt')
    return open(f).read()