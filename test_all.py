from postgrespy.models import Model
from postgrespy.fields import TextField, IntegerField, BooleanField


class Student(Model):
    name = TextField()
    age = IntegerField()
    is_male = BooleanField()

    class Meta:
        table = 'students'


def test_sql_model():
    peter = Student(name='Peter', age=15)
    peter.save()
    assert peter.age == 15

    still_peter = Student(id=peter.id)
    assert still_peter.name == 'Peter'

    tom = Student(name='Tom', age=27)
    tom.save()

    still_tom = Student(id=tom.id)
    assert still_tom.age == 27


def test_boolean_field():
    transgender = Student(name='HG', age=27, is_male=True)
    transgender.save()
    assert transgender.is_male == True

    transgender.is_male = False
    transgender.save()

    still_trangender = Student(id=transgender.id)
    assert still_trangender.is_male == False


def test_select_query():
    peter = Student.getone('name = %s', ('Peter',))
    assert peter.age == 15
