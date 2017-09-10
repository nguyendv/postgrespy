from postgrespy.db import get_conn_cur, close
from postgrespy import UniqueViolatedError
from postgrespy.fields import BaseField, JsonBField, IntegerField
from postgrespy.queries import Select
from jinja2 import Template
from psycopg2 import DatabaseError
import json
import warnings



class Model(object):
    """
    Base class for SqlModel

    IMPORTANT!: Every child has a implicit `id` row.
    """

    def __init__(self, id=None, **kwargs):
        self.id = id
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

        self.fields = set()
        for k in dir(self):
            if issubclass(type(getattr(self, k)), BaseField):
                self.fields.add(k)

    def __setattr__(self, name, value):
        if name in dir(self):
            if value is not None:
                field_cls = type(getattr(self, name))
                if name == 'id':
                    field_cls = IntegerField
                super().__setattr__(name, field_cls(value))
        else:
            super().__setattr__(name, value)

    def save(self):
        """Insert if id is None.
        Update if otherwise
        IMPORTANT: this is a 'dumb' method. You need to check for
        any constraint or handle exception before/after calling me.
        and DON't add new attributes after an object is created.
        """
        warnings.warn("DEPRECATED from September 2017. Use update(self, **kwargs) instead", DeprecationWarning)
        if self.id is None:
            self._insert()
        else:
            self._update()

    @classmethod
    def insert(cls, **kwargs):
        """ Execute the INSERT query
        :param: kwargs: list of key=value, where
                key is one field of the table,
                value must be a Python builtin type, not my custom types defined in fields.py: int, string, datetime, dict, etc."""
        conn, cur = get_conn_cur()

        template = Template('INSERT INTO {{table}}\n'
                            '( {{columns}} )\n'
                            'VALUES ( {{placeholders}} )\n'
                            'RETURNING id')

        """Prepare placeholders"""
        temp_arr = []
        for k,v in kwargs.items():
            if type(v) is list and type(v[0]) is dict:
                # https://github.com/psycopg/psycopg2/issues/585
                #https://stackoverflow.com/questions/31641894/convert-python-list-of-dicts-into-postgresql-array-of-json
                temp_arr.append('%s::jsonb[]')
            else: 
                temp_arr.append('%s')
        placeholders = ','.join(temp_arr)
        
        """Render and execute the statement"""
        stmt = template.render(table=cls.Meta.table,
                               columns=','.join(kwargs.keys()),
                               placeholders=placeholders
                               )
        ret = None

        try:
            values = tuple(val for val in kwargs.values())
            cur.execute(stmt, values)
            id = cur.fetchone()[0]
            conn.commit()
            ret = cls(id, **kwargs)
        except DatabaseError as e:
            conn.rollback()
            if e.pgcode == '23505':
                """
                23505: PostgreSQL error code: unique violation
                https://www.postgresql.org/docs/9.6/static/errcodes-appendix.html
                """
                raise UniqueViolatedError()
            else:
                raise NotImplementedError(
                    'Unhandled error. Need to check.')

        close(conn, cur)
        return ret

    def update(self, **kwargs):
        """Execute the update query
        :param: kwargs: list of key=value, where
                key is one field of the table,
                value must be a Python builtin type, not my custom types defined in fields.py: int, string, datetime, dict, etc."""
        conn, cur = get_conn_cur()

        template = Template('UPDATE {{table}} '
                            'SET {{ field_value_pairs }} '
                            'WHERE id = %s')

        """Prepare the field value pairs"""
        temp_arr = []
        for k,v in kwargs.items():
            if type(v) is list and type(v[0]) is dict:
                # https://github.com/psycopg/psycopg2/issues/585
                #https://stackoverflow.com/questions/31641894/convert-python-list-of-dicts-into-postgresql-array-of-json
                temp_arr.append(k + ' = %s::jsonb[]')
            else: 
                temp_arr.append(k + ' = %s')
        field_value_pairs = ','.join(temp_arr)

        """Render and execute the statement"""
        stmt = template.render(table=self.Meta.table, field_value_pairs=field_value_pairs)
        cur.execute(stmt, list(kwargs.values()) + [self.id])

        conn.commit()
        close(conn, cur)

        for k,v in kwargs.items():
            setattr(self, k, v)

    # DEPRECATED, use update(cls, **kwargs) instead
    def _update(self):
        """Execute the UPDATE query"""
        warnings.warn("_update(self) deprecated from 09/2017, use update(self, **kwargs) instead", DeprecationWarning)
        conn, cur = get_conn_cur()

        template = Template('UPDATE {{table}}\n'
                            'SET {{ field_value_pairs }} \n'
                            'WHERE id = %s')
        stmt = template.render(table=self.Meta.table,
                               field_value_pairs=','.join(
                                   f + '=%s' for f in self.fields))
        values = []
        for f in self.fields:
            if getattr(self, f) is None:
                values.append(None)
            else:
                values.append(getattr(self, f).value)
        cur.execute(stmt, values + [self.id])

        conn.commit()
        close(conn, cur)

    @classmethod
    def fetchone(cls, **kwargs):
        """Syntactic sugar for Select().fetchone()"""
        wheres = [k + '=%s' for k in kwargs.keys()]
        if len(kwargs) > 0:
            where = ' and '.join(wheres)
            values = tuple(kwargs.values())
        else:
            where = None
            values = None
        with Select(cls, where) as select:
            select.execute(values)
            one = select.fetchone()
            if one is None:
                return None
        return one

    @classmethod
    def fetchall(cls, **kwargs):
        """Syntactic sugar for Select().fetchall()"""
        wheres = [k + '=%s' for k in kwargs.keys()]
        if len(kwargs) > 0:
            where = ' and '.join(wheres)
            values = tuple(kwargs.values())
        else:
            where = None
            values = None
        with Select(cls, where) as select:
            select.execute(values)
            return select.fetchall()

    @classmethod
    def fetchmany(cls, size, **kwargs):
        """Syntactic sugar for Select().fetchmany()"""
        wheres = [k + '=%s' for k in kwargs.keys()]
        if len(kwargs) > 0:
            where = ' and '.join(wheres)
            values = tuple(kwargs.values())
        else:
            where = None
            values = None
        with Select(cls, where) as select:
            select.execute(values)
            return select.fetchmany(size)

    def delete(self):
        """
        Delete the row from database.
        """
        conn, cur = get_conn_cur()
        template = Template('DELETE FROM {{table}}\n'
                            'WHERE id = %s')
        stmt = template.render(table=self.Meta.table)
        cur.execute(stmt, (self.id,))
        conn.commit()
        close(conn, cur)
    
    # DEPRECATED, use ::insert() instead
    def _insert(self):
        """ Execute the INSERT query"""
        warnings.warn("DEPRECATED, use ::insert() instead", DeprecationWarning)
        conn, cur = get_conn_cur()

        template = Template('INSERT INTO {{table}}\n'
                            '( {{columns}} )\n'
                            'VALUES ( {{placeholders}} )\n'
                            'RETURNING id')

        stmt = template.render(table=self.Meta.table,
                               columns=','.join(self.fields),
                               placeholders=','.join('%s'
                                                     for f in self.fields)
                               )
        try:
            values = []
            for f in self.fields:
                if type(getattr(self, f)) == JsonBField:
                    values.append(json.dumps(getattr(self, f).value))
                else:
                    values.append(getattr(self, f).value)
            cur.execute(stmt, values)
            self.id = cur.fetchone()[0]
            conn.commit()
        except DatabaseError as e:
            conn.rollback()
            if e.pgcode == '23505':
                """
                23505: PostgreSQL error code: unique violation
                https://www.postgresql.org/docs/9.6/static/errcodes-appendix.html
                """
                raise UniqueViolatedError()
            else:
                raise NotImplementedError(
                    'Unhandled error. Need to check.')
        close(conn, cur)


