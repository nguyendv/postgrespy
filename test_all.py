from .models import Model
from .fields import TextField, IntegerField


class Student(Model):
    name = TextField()
    age = IntegerField()

    class Meta:
        table = 'students'


def test_sql_model():
    peter = Student(name='Peter', age=15)
    peter.save()

    still_peter = Student(id=peter.id)
    assert still_peter.name == 'Peter'

    tom = Student(name='Tom', age=27)
    tom.save()

    still_tom = Student(id=tom.id)
    assert still_tom.age == 27


def test_select_query():
    peter = Student.getone('name = %s', ('Peter',))
    assert peter.age == 15
