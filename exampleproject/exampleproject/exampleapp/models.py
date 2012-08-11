import datetime
from django_mongokit import connection
from django_mongokit.document import DjangoDocument


# Create your models here.
class Talk(DjangoDocument):
    collection_name = 'talks'
    structure = {
        'topic': unicode,
        'when': datetime.datetime,
        'tags': list,
        'duration': float,
    }

    required_fields = ['topic', 'when', 'duration']

    use_dot_notation = True

connection.register([Talk])
