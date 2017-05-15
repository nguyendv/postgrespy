from postgrespy.models import Model
from postgrespy.fields import TextField, IntegerField, BooleanField, JsonBField
from postgrespy.queries import Select


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


def test_save_load_delete():
    peter = Student(name='Peter', age=15)
    peter.save()
    assert peter.age == 15

    still_peter = Student(id=peter.id)
    print('Peter: ', still_peter.name)
    assert still_peter.name == 'Peter'
    assert still_peter.age == 15

    another_peter = Student(name='Peter', age=17)
    another_peter.save()

    with Select(Student, 'name=%s') as select:
        select.execute(('Peter', ))
        two_peters = select.fetchall()
        assert len(two_peters) == 2

    peter.delete()
    still_peter.delete()
    another_peter.delete()

    with Select(Student, 'name=%s') as select:
        select.execute(('Peter', ))
        none_peters = select.fetchall()
        assert len(none_peters) == 0


def test_boolean_field():
    transgender = Student(name='HG', age=27, is_male=True)
    transgender.save()
    assert transgender.is_male == True

    transgender.is_male = False
    transgender.save()

    still_trangender = Student(id=transgender.id)
    assert still_trangender.is_male == False

    transgender.delete()
    still_trangender.delete()


def test_jsonb_field():
    tom = Student(name='Tom')
    tom.save()
    meth = Product(name='meth', owner_id=tom.id, detail={
        'color': 'red',
        'weight': 5
    })
    meth.save()

    still_meth = Product(id=meth.id)
    print(still_meth.detail)
    assert(meth.detail['color'] == 'red')

    meth.delete()
    still_meth.delete()
    tom.delete()


def test_get_all():
    phil = Student(name='Phil', age=27)
    phil.save()
    thor = Student(name='Thor', age=33)
    thor.save()

    all_adults = Student.getall()
    assert len(all_adults) == 2
    phil.delete()
    thor.delete()


def test_joins():
    pass
