""" Mock model definitions for unit testing"""

from . import Model
from postgrespy.fields import TextField, BooleanField

class Student(Model):
    name = TextField() 
    is_smart = BooleanField()

    class Meta:
        table = 'students'

