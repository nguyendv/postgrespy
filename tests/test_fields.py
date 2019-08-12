""" Unittest for postgresql/fields.py"""
from unittest import TestCase
from datetime import datetime
from .models import Movie, Entry, Student, Product


class ArrayFieldTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        for movie in Movie.fetchall():
            movie.delete()

    def test_array_field(self):
        Movie.insert(name="Wonder Woman", casts=["Gal Gadot", "Chris Pine"])

        still_wonder_woman = Movie.fetchone(name="Wonder Woman")
        assert len(still_wonder_woman.casts) == 2
        assert still_wonder_woman.casts[1] == "Chris Pine"


class ArrayOfJsonTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        for movie in Movie.fetchall():
            movie.delete()

    def test_array_of_json_field(self):
        Movie.insert(
            name="Wonder Woman",
            casts=["Gal Gadot", "Chris Pine"],
            earning=[{"country": "USA", "amount": 1000}],
            trivia=[
                {
                    "gid": "a31e4ed0-950f-11e7-a6d6-51c771a79848",
                    "ip": "192.168.1.100",
                    "name": "Network0_Instance1",
                    "network": {
                        "cidr": "192.168.1.0/24",
                        "gid": "9ecb9680-950f-11e7-a6d6-51c771a79848",
                        "name": "Network0",
                        "type": "NetworkNode",
                        "x": 444.515625,
                        "y": 38,
                    },
                    "target": {
                        "gid": "a0b935b0-950f-11e7-a6d6-51c771a79848",
                        "image": "Ubuntu-Server-16.04-x64",
                        "links": [],
                        "name": "Instance1",
                        "status": None,
                        "type": "Instance",
                        "x": 527.515625,
                        "y": 362,
                    },
                    "type": "NetworkLink",
                }
            ],
        )

        # Test len()
        still_wonder_woman = Movie.fetchall(name="Wonder Woman")[0]
        assert len(still_wonder_woman.earning) == 1
        assert still_wonder_woman.earning[0]["country"] == "USA"

        assert len(still_wonder_woman.trivia) == 1
        assert still_wonder_woman.trivia[0]["ip"] == "192.168.1.100"

        # Test iteration
        trivias = []
        for t in still_wonder_woman.trivia:
            trivias.append(t)
        assert len(trivias) == 1

        # Test save
        new_earning = [{"country": "USA", "amount": 100}]
        still_wonder_woman.update(earning=new_earning)

        still_wonder_woman = Movie.fetchall(name="Wonder Woman")[0]
        assert len(still_wonder_woman.earning) == 1
        assert still_wonder_woman.earning[0]["amount"] == 100


class DateTimeFieldTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        for entry in Entry.fetchall():
            entry.delete()

    def test_date_time_field(self):
        now = datetime.now()
        abc = Entry.insert(body="ABC", updated=now)

        still_abc = Entry.fetchone(id=abc.id)
        updated = still_abc.updated.value

        assert (
            all(
                updated.year == now.year,
                updated.month == now.month,
                updated.day == now.day,
                updated.hour == now.hour,
                updated.minute == now.minute,
                updated.second == now.second,
            )
            is True
        )


class BooleanTestCase(TestCase):
    def setUp(self):
        self.transgender = Student.insert(name="HG", age=27, is_male=True)

    def test_boolean_field(self):

        assert self.transgender.is_male is True

        self.transgender.update(is_male=False)

        still_trangender = Student.fetchone(id=self.transgender.id)
        assert still_trangender.is_male is False

        still_trangender.delete()

    def tearDown(self):
        for student in Student.fetchall():
            student.delete()


class JsonBTestCase(TestCase):
    def setUp(self):
        self.tom = Student.insert(name="Tom")
        self.meth = Product.insert(
            name="meth", owner_id=self.tom.id, detail={"color": "red", "weight": 5}
        )

    def test_jsonb_field(self):
        assert self.meth.detail["color"] == "red"
        new_detail = self.meth.detail
        new_detail["price"] = 5
        self.meth.update(detail=new_detail.value)

        meth2 = Product.fetchone(id=self.meth.id)
        assert meth2.detail["price"] == 5

    def tearDown(self):
        for student in Student.fetchall():
            student.delete()
