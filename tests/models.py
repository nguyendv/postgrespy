from postgrespy.models import Model
from postgrespy.fields import TextField, IntegerField, BooleanField, JsonBField, ArrayField, DateTimeField

class Student(Model):
    name = TextField()
    age = IntegerField()
    is_male = BooleanField()

    class Meta:
        table = 'students'


class Product(Model):
    name = TextField()
    owner_id = IntegerField()
    detail = JsonBField()

    class Meta:
        table = 'products'


class Car(Model):
    name = TextField()
    owner_id = IntegerField()

    class Meta:
        table = 'cars'

class Movie(Model):
    name = TextField()
    trivia = ArrayField()
    casts = ArrayField()
    earning = ArrayField()

    class Meta:
        table = 'movies'


class Entry(Model):
    body = TextField()
    updated = DateTimeField()

    class Meta:
        table = 'entries'

