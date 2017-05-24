from postgrespy.models import Model
from postgrespy.fields import TextField, IntegerField, BooleanField, JsonBField
from postgrespy.queries import Select, Join


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
    assert(type(peter.age) == IntegerField)
    assert peter.age == 15

    still_peter = Student(id=peter.id)
    assert(type(still_peter.age) == IntegerField)
    still_peter.age = 16
    still_peter.save()
    assert still_peter.name == 'Peter'
    assert still_peter.age == 16

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

    assert(meth.detail['color'] == 'red')

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
    tom = Student(name='Tom', age=20)
    jerry = Student(name='Jerry', age=20)
    bob = Student(name='Bob', age=20)
    tom.save()
    jerry.save()
    bob.save()

    weed = Product(name='weed', owner_id=tom.id, detail={})
    smoke = Product(name='smoke', owner_id=tom.id, detail={})
    book = Product(name='book', owner_id=jerry.id, detail={})
    weed.save()
    smoke.save()
    book.save()

    with Join(Student, 'INNER JOIN', Product, 'students.id = products.owner_id') as join:
        join.execute()
        ret = join.fetchall()

    assert len(ret) == 3
    still_tom, still_smoke = ret[1]
    assert still_tom.name == 'Tom'
    assert still_smoke.name == 'smoke'

    tom.delete()
    jerry.delete()
    bob.delete()

    assert len(Product.getall()) == 0
