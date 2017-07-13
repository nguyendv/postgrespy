from postgrespy.models import Model
from postgrespy.fields import TextField, IntegerField, BooleanField, JsonBField, ArrayField
from postgrespy.queries import Select, Join
from unittest import TestCase


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
    casts = ArrayField()

    class Meta:
        table = 'movies'


class SaveLoadDeleteTestCase(TestCase):
    def setUp(self):
        self.peter = Student(name='Peter', age=15)
        self.peter.save()
        self.still_peter = Student.fetchone(id=self.peter.id)
        self.no_one = Student.fetchone(id=999, name='hehe')

        self.another_peter = Student(name='Peter', age=17)
        self.another_peter.save()

    def test_save_load_delete(self):

        assert(type(self.peter.age) == IntegerField)
        assert self.peter.age == 15

        assert(type(self.still_peter.age) == IntegerField)
        self.still_peter.age = 16
        self.still_peter.save()
        assert self.still_peter.name == 'Peter'
        assert self.still_peter.age == 16

        with Select(Student, 'name=%s') as select:
            select.execute(('Peter', ))
            two_peters = select.fetchall()
            assert len(two_peters) == 2

        assert self.no_one is None

    def tearDown(self):
        self.peter.delete()
        self.still_peter.delete()
        self.another_peter.delete()


class BooleanTestCase(TestCase):
    def setUp(self):
        self.transgender = Student(name='HG', age=27, is_male=True)
        self.transgender.save()

    def test_boolean_field(self):

        assert self.transgender.is_male == True

        self.transgender.is_male = False
        self.transgender.save()

        still_trangender = Student.fetchone(id=self.transgender.id)
        assert still_trangender.is_male == False

        still_trangender.delete()

    def tearDown(self):
        self.transgender.delete()


class JsonBTestCase(TestCase):
    def setUp(self):
        self.tom = Student(name='Tom')
        self.tom.save()
        self.meth = Product(name='meth', owner_id=self.tom.id, detail={
            'color': 'red',
            'weight': 5
        })
        self.meth.save()

    def test_jsonb_field(self):
        assert(self.meth.detail['color'] == 'red')
        self.meth.detail['price'] = 5
        self.meth.save()

        meth2 = Product.fetchone(id=self.meth.id)
        assert(meth2.detail['price'] == 5)

    def tearDown(self):
        self.tom.delete()


class FetchAllTestCase(TestCase):
    def setUp(self):
        self.phil = Student(name='Phil', age=27)
        self.phil.save()
        self.thor = Student(name='Thor', age=33)
        self.thor.save()

    def test_get_all(self):
        all_adults = Student.fetchall()
        all_thors = Student.fetchall(name='Thor', age=33)
        assert len(all_adults) == 2
        assert len(all_thors) == 1

    def tearDown(self):
        self.phil.delete()
        self.thor.delete()


def JoinTestCase(TestCase):
    def setUp(self):
        self.tom = Student(name='Tom', age=20)
        self.jerry = Student(name='Jerry', age=20)
        self.bob = Student(name='Bob', age=20)
        self.tom.save()
        self.jerry.save()
        self.bob.save()

        self.weed = Product(name='weed', owner_id=self.tom.id, detail={})
        self.smoke = Product(name='smoke', owner_id=self.tom.id, detail={})
        self.book = Product(name='book', owner_id=self.jerry.id, detail={})

        self.weed.save()
        self.smoke.save()
        self.book.save()

        self.toyota = Car(name='Toyota', owner_id=self.tom.id)
        self.nissan = Car(name='Nissan', owner_id=self.tom.id)
        self.toyota.save()
        self.nissan.save()

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


class ArrayFieldTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        for movie in Movie.fetchall():
            movie.delete()

    def test_array_field(self):
        wonder_woman = Movie(name="Wonder Woman", casts=[
                             "Gal Gadot", "Chris Pine"])
        wonder_woman.save()

        still_wonder_woman = Movie.fetchone(name="Wonder Woman")
        assert still_wonder_woman.casts[1] == "Chris Pine"
