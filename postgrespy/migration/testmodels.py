from postgrespy.models import Model
from postgrespy.fields import IntegerField, TextField, BooleanField

class Student(Model):
    name = TextField()
    age = IntegerField()

    class Meta:
        table = 'students'

class Book(Model):
    name = TextField()
    year = IntegerField()

    class Meta:
        table = 'books'

