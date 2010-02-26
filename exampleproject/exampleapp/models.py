import datetime
from django_mongokit import DjangoDocument

# Create your models here.
class Talk(DjangoDocument):
    collection_name = 'talks'
    structure = {
        'topic': unicode,
        'when': datetime.datetime,
        'tags': list,
        'duration': float,
    }
    
    use_dot_notation = True
    
    
