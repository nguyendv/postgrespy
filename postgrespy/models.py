from postgrespy.db import get_conn_cur, close
from postgrespy import UniqueViolatedError
from postgrespy.fields import BaseField, JsonBField, IntegerField
from postgrespy.queries import Select
from jinja2 import Template
from psycopg2 import DatabaseError
import json


class Model(object):
    """
    Base class for SqlModel

    IMPORTANT!: Every child has a implicit `id` row.
    """

    def __init__(self, id=None, **kwargs):
        self.id = id
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

        self.fields = []
        for k in dir(self):
            if issubclass(type(getattr(self, k)), BaseField):
                self.fields.append(k)

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
        """
        Insert if id is None.
        Update if otherwise
        IMPORTANT: this is a 'dumb' method. You need to check for
        any constraint or handle exception before/after calling me.
        and DON't add new attributes after an object is created.
        """
        if self.id is None:
            self._insert()
        else:
            self._update()

    @classmethod
    def fetchone(cls, **kwargs):
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

    def _insert(self):
        """ Execute the INSERT query"""
        conn, cur = get_conn_cur()

        template = Template('INSERT INTO {{table}}\n'
                            '( {{fields}} )\n'
                            'VALUES ( {{placeholders}} )\n'
                            'RETURNING id')

        stmt = template.render(table=self.Meta.table,
                               fields=','.join(self.fields),
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

    def _update(self):
        """ Execute the UPDATE query"""
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
                if type(getattr(self, f)) == JsonBField:
                    values.append(json.dumps(getattr(self, f).value))
                else:
                    values.append(getattr(self, f).value)
        cur.execute(stmt, values + [self.id])

        conn.commit()
        close(conn, cur)
