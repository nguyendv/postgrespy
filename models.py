from postgrespy.db import get_conn_cur, close, UniqueViolatedError
from postgrespy.fields import BaseField, BooleanField, JsonBField
from postgrespy.queries import Select
from jinja2 import Template
from psycopg2 import DatabaseError
from typing import Tuple
import json


class Model(object):
    """
    Base class for SqlModel

    IMPORTANT!: Every child has a implicit `id` row.
    """

    def __init__(self, id=None, **kwargs):
        self.id = id
        for k in kwargs.keys():
            if k in dir(self):
                """ Cast the value to the correct type, then rewrite that key to that value"""
                cls = type(getattr(self, k))
                setattr(self, k, cls(kwargs[k]))
            else:
                setattr(self, k, kwargs[k])

        self.fields = []
        for k in dir(self):
            if issubclass(type(getattr(self, k)), BaseField) and k != 'id':
                self.fields.append(k)

        if self.id is not None:
            self._load()

    def __setattr__(self, name, value):
        if type(value) == bool:
            setattr(self, name, BooleanField(value))
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
    def getall(cls):
        with Select(cls) as select:
            select.execute()
            ret = select.fetchall()
        return ret

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

    def _load(self):
        """
        Load the row from database, given the id
        Required id is not None
        """
        with Select(self.__class__, 'id=%s') as select:
            select.execute((self.id,))
            ret = select.fetchone()
            for f in self.fields:
                setattr(self, f, getattr(ret, f))

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
        for f in self.fields:
            print(f, getattr(self, f))
        values = [getattr(self, f).value for f in self.fields]
        cur.execute(stmt, values + [self.id])

        conn.commit()
        close(conn, cur)
