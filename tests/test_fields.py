""" Contain tests for some postgrespy.fields class"""

from unittest import TestCase
from datetime import datetime

from postgrespy.fields import TextField, ArrayField, DateTimeField
from postgrespy.models import Model

import psycopg2.extras
from psycopg2.extras import Json

class Movie(Model):
    name = TextField()
    casts = ArrayField()
    earning = ArrayField()

    class Meta:
        table = 'movies'


class Entry(Model):
    body = TextField()
    updated = DateTimeField()

    class Meta:
        table = 'entries'


class ArrayFieldTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        for movie in Movie.fetchall():
            movie.delete()

    def test_array_field(self):
        wonder_woman = Movie.insert(name="Wonder Woman", casts=[
            "Gal Gadot", "Chris Pine"])

        still_wonder_woman = Movie.fetchone(name="Wonder Woman")
        assert still_wonder_woman.casts[1] == "Chris Pine"


class ArrayOfJsonTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        for movie in Movie.fetchall():
            movie.delete()

    def test_array_of_json_field(self):
        pass
        wonder_woman = Movie.insert(name="Wonder Woman", casts=[
            "Gal Gadot", "Chris Pine"], 
            earning=[{"country": "USA", "amount": 1000}]
            )

        still_wonder_woman = Movie.fetchone(name="Wonder Woman")
        assert still_wonder_woman.earning[0]['country'] == 'USA'


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

        assert updated.year == now.year and \
            updated.month == now.month and \
            updated.day == now.day and \
            updated.hour == now.hour and \
            updated.minute == now.minute and \
            updated.second == now.second
