from postgrespy.fields import BooleanField, TextField
from postgrespy.models import Model
from .testmodels import Student as OldStudent, Book
from . import CreateTable, DropColumn, AddColumn
from . import models_to_migrations, migrations_to_models, _find_model_by_name

class Student(Model):
    name = TextField()
    is_smart= BooleanField()

    class Meta:
        table = 'students'

create_student = CreateTable(OldStudent)
sql = """
CREATE TABLE students (
    age         integer,
    name        text
);
"""
def test_to_sql():
    assert ''.join(sql.split()) == ''.join(create_student.to_sql().split())

def test_models_to_migrations():
    assert models_to_migrations([Student,], None) == [CreateTable(Student)]
    assert models_to_migrations([Student], [CreateTable(OldStudent)]) == [
            CreateTable(OldStudent), DropColumn(OldStudent, 'age'), AddColumn(OldStudent, 'is_smart', BooleanField())
        ]

def test_migrations_to_models():
    migrations = [CreateTable(Student)]
    assert [Student,] == migrations_to_models(migrations)

    migrations = [
            CreateTable(OldStudent), 
            DropColumn(OldStudent, 'age'), 
            AddColumn(Student, 'is_smart', BooleanField())
    ]
    assert [Student.schema_presentation(),] == [
                model.schema_presentation() for model in migrations_to_models(migrations)
            ]

def test_find_model_by_name():
    models = [Student, Book]
    assert _find_model_by_name(models, Student.tablename()) == 0
    assert _find_model_by_name(models, Book.tablename()) == 1
