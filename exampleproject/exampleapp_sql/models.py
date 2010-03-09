import datetime
from django.db import models

class ArrayField(models.CharField):
    
    __metaclass__ = models.SubfieldBase
    
    
    description = "basic field for storing string arrays"
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 200
        super(ArrayField, self).__init__(*args, **kwargs)
        
    def to_python(self, value):
        if isinstance(value, list):
            return value
        
        return value.split('|')
    
    def get_prep_value(self, value):
        return '|'.join(value)
    

# Create your models here.
class Talk(models.Model):
    topic = models.CharField(max_length=200)
    when = models.DateTimeField()
    tags = ArrayField(max_length=200)
    duration = models.FloatField()
    
    
