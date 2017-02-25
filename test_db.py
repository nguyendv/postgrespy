from db import SqlModel, get_pool

pool = get_pool()


class Student(SqlModel):
    _table_ = 'students'
    _cols_ = ('name', 'age')


def test_sql_model():
    peter = Student(name='Peter', age=15)
    peter.save()

    still_peter = Student(id=peter.id)
    assert still_peter.name == 'Peter'
