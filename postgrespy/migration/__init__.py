from postgrespy.models import Model
from postgrespy.fields import BaseField

from typing import List

class Migration(object):
    def __init__(self, model: Model):
        self.model = model

    def __eq__(self, other: object):
        if isinstance(other, self.__class__):
            return self.model.tablename() == other.model.tablename() and (
                {k:v for k,v in self.__dict__.items() if k!='model'} == 
                {k:v for k,v in other.__dict__.items() if k!='model'} )
        return NotImplemented


class CreateTable(Migration):
    def to_sql(self) -> str:
        table_name : str = self.model.tablename()
        
        sql = """
CREATE TABLE {table_name} (
{column_definitions}
);
"""
        columns = self.model._get_columns()
        lines = ['  {name}          {column_type}'.format(name=col[0], column_type=col[1]) for col in columns]
        return sql.format(table_name=table_name, column_definitions=',\n'.join(lines))

    def execute(self):
        pass

class DropTable(Migration):
    pass

class DropColumn(Migration):
    def __init__(self, model:Model, column_name: str):
        super().__init__(model)
        self.column_name = column_name

    def execute(self):
        pass

class AddColumn(Migration):
    def __init__(self, model:Model, column_name: str, field_type: BaseField):
        super().__init__(model)
        self.column_name = column_name
        self.column_type = field_type

class SetColumnType(Migration):
    pass

class RenameColumn(Migration):
    pass

def models_to_migrations(models: List[Model], existing_migrations: List[Migration] = None) -> List[Migration]:
    """ Create migrations from a lsit of exisint migrations and a list of new model definition"""
    if existing_migrations is None:
        return [CreateTable(model) for model in models]
    else:
        migrations : List[Migration] = []
        # get the list of models from the existing list of migrations (old_models)
        old_models : List[Model] = migrations_to_models(existing_migrations)

        for model in models:
            idx = _find_model_by_name(old_models, model.tablename())
            if idx >= 0:
                # - TODO: if model in old_models: make a list of DropColumn and AddColumn migrations
                
                pass
            else:
                migrations.append(CreateTable(model))

        return migrations
                

def migrations_to_models(migrations: List[Migration]) -> List[Model]:
    """ Create a list of final models from a list of migrations"""
    models : List[Model] = []
    for migration in migrations:
        if isinstance(migration, CreateTable):
            models.append(migration.model)

        elif isinstance(migration, DropColumn):
            index = _find_model_by_name(models, migration.model.tablename())
            assert index >= 0, "any migration other than CreateTable should operate on an existing model"
            delattr(models[index], migration.column_name)

        elif isinstance(migration, AddColumn):
            index = _find_model_by_name(models, migration.model.tablename())
            assert index >= 0, "any migration other than CreateTable should operate on an existing model"
            setattr(models[index], migration.column_name, migration.column_type)
    return models

def migrations_model_to_model(old_model: Model, new_model: Model):
    """ Generate a list of migrations to migrate from an old model to a new model"""
    assert old_model.tablename() == new_model.tablename() \
        , "this function is only for two model definition of a same table"

def _find_model_by_name(models: List[Model], name: str) -> int:
    """ Find the index of the target_model from a list"""
    for idx, model in enumerate(models):
        if model.tablename() == name:
            return idx
    return -1
