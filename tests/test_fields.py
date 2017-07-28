""" Contain tests for some postgrespy.fields class"""

from unittest import TestCase
from postgrespy.fields import TextField, ArrayField
from postgrespy.models import Model


class Movie(Model):
    name = TextField()
    casts = ArrayField()

    class Meta:
        table = 'movies'


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
