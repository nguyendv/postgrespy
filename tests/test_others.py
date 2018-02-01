from postgrespy.queries import Select, Join
from postgrespy.fields import IntegerField
from unittest import TestCase
from .models import Student, Product, Car


class SaveLoadDeleteTestCase(TestCase):
    def setUp(self):
        self.peter = Student.insert(name='Peter', age=15)
        self.still_peter = Student.fetchone(id=self.peter.id)

        self.no_one = Student.fetchone(id=999, name='hehe')

        self.another_peter = Student.insert(name='Peter', age=17)

    def test_save_load_delete(self):

        assert(type(self.peter.age) == IntegerField)
        assert self.peter.age == 15

        assert(type(self.still_peter.age) == IntegerField)
        self.still_peter.update(age=16)

        assert self.still_peter.name == 'Peter'
        assert self.still_peter.age == 16

        with Select(Student, 'name=%s') as select:
            select.execute(('Peter', ))
            two_peters = select.fetchall()
            assert len(two_peters) == 2

        assert self.no_one is None

    def tearDown(self):
        for student in Student.fetchall():
            student.delete()


class ModelFetchTestCase(TestCase):
    def setUp(self):
        self.phil = Student.insert(name='Phil', age=27)
        self.thor = Student.insert(name='Thor', age=33)
        self.stark = Student.insert(name='Stark', age=40)

    def test_fetch_all(self):
        all_adults = Student.fetchall()
        all_thors = Student.fetchall(name='Thor', age=33)
        assert len(all_adults) == 3
        assert len(all_thors) == 1

    def test_fetch_many(self):
        many = Student.fetchmany(2)
        assert len(many) == 2

    def tearDown(self):
        for student in Student.fetchall():
            student.delete()


def SelectTestCase(TestCase):
    def setUp(self):
        Student.insert(name='Pete', age=22)
        Student.insert(name='John', age=23)
        Student.insert(name='Dan', age=27)
        Student.insert(name='Jeff', age=19)
        Student.insert(name='Vin', age=19)

    def test_select_with_order():
        with Select(Student) as select:
            select.order_by("age DESC", "name")
            students = select.fetchall()
            Vin = students[len(students) - 1]
            assert Vin.name == 'Vin'

    def tearDown(self):
        for student in Student.fetchall():
            student.delete()


def JoinTestCase(TestCase):
    def setUp(self):
        self.tom = Student.insert(name='Tom', age=20)
        self.jerry = Student.insert(name='Jerry', age=20)
        self.bob = Student.insert(name='Bob', age=20)

        self.weed = Product.insert(
            name='weed', owner_id=self.tom.id, detail={})
        self.smoke = Product.insert(
            name='smoke', owner_id=self.tom.id, detail={})
        self.book = Product.insert(
            name='book', owner_id=self.jerry.id, detail={})

        self.toyota = Car.insert(name='Toyota', owner_id=self.tom.id)
        self.nissan = Car.insert(name='Nissan', owner_id=self.tom.id)

    def test_joins(self):

        with Join(Student, 'INNER JOIN', Product, 'students.id = products.owner_id') as join:
            join.execute()
            ret = join.fetchall()

        assert len(ret) == 3

        still_tom, still_smoke = ret[1]
        assert still_tom.name == 'Tom'
        assert still_smoke.name == 'smoke'

        with Join(Student, 'INNER JOIN', Product, 'students.id = products.owner_id',
                  'INNER JOIN', Car, 'students.id = cars.owner_id') as join:
            join.execute()
            ret = join.fetchall()
        assert len(ret) == 4

    def tearDown(self):
        self.tom.delete()
        self.jerry.delete()
        self.bob.delete()


class NothingTestCase(TestCase):
    """This test case ensures that all objects have been deleted"""

    def setUp(self):
        pass

    def test_nothing(self):
        assert (len(Student.fetchall()) == 0)
        assert (len(Product.fetchall()) == 0)
        assert (len(Car.fetchall()) == 0)

    def tearDown(self):
        pass
