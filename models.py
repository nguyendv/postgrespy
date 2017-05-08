from postgrespy.db import get_pool, UniqueViolatedError
from postgrespy.fields import BaseField, BooleanField, JsonBField
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
    def getone(cls, where: str = None, values: Tuple = None):
        pool = get_pool()
        conn = pool.getconn()
        cur = conn.cursor()
        fields = [f for f in dir(cls) if not f.startswith(
            '__') and issubclass(type(getattr(cls, f)), BaseField)]
        fields = fields + ['id']
        stmt = 'SELECT ' + ','.join(fields) + ' FROM ' + cls.Meta.table
        if where is not None:
            stmt = stmt + ' WHERE ' + where
        print(stmt)
        cur.execute(stmt, values)
        row = cur.fetchone()
        ret = cls()
        for i, f in enumerate(fields):
            setattr(ret, f, row[i])
        return ret

    @classmethod
    def getall(cls, where: str = None, values: Tuple = None):
        pool = get_pool()
        conn = pool.getconn()
        cur = conn.cursor()
        fields = [f for f in dir(cls) if not f.startswith(
            '__') and issubclass(type(getattr(cls, f)), BaseField)]
        fields = fields + ['id']
        stmt = 'SELECT ' + ','.join(fields) + ' FROM ' + cls.Meta.table
        if where is not None:
            stmt = stmt + ' WHERE ' + where
        print(stmt)
        cur.execute(stmt, values)
        rows = cur.fetchall()
        ret = []
        for row in rows:
            r = cls()
            for i, f in enumerate(fields):
                setattr(r, f, row[i])
            ret.append(r)
        return ret

    def delete(self):
        """
        Delete the row from database.
        """
        pool = get_pool()
        conn = pool.getconn()
        cur = conn.cursor()
        template = Template('DELETE FROM {{table}}\n'
                            'WHERE id = %s')
        stmt = template.render(table=self.Meta.table)
        cur.execute(stmt, (self.id,))
        conn.commit()
        cur.close()
        pool.putconn(conn)

    def _load(self):
        """
        Load the row from database
        Required id is not None
        """
        assert self.id is not None
        pool = get_pool()
        conn = pool.getconn()
        cur = conn.cursor()
        template = Template('SELECT {{fields}}\n'
                            'FROM {{table}}\n'
                            'WHERE id=%s\n'
                            'LIMIT 1')
        stmt = template.render(table=self.Meta.table,
                               fields=','.join(self.fields))
        cur.execute(stmt, (self.id,))
        row = cur.fetchone()
        try:
            i = 0
            for field in self.fields:
                setattr(self, field, row[i])
                i = i + 1
        except TypeError as e:
            # cannot access row[i]
            if str(e) == '\'NoneType\' object is not subscriptable':
                raise NotImplementedError('New error. Need to check')
            else:
                raise NotImplementedError('New error. Need to check')

        cur.close()
        pool.putconn(conn)

    def _insert(self):
        """ Execute the INSERT query"""
        pool = get_pool()
        conn = pool.getconn()
        cur = conn.cursor()

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
        cur.close()
        pool.putconn(conn)

    def _update(self):
        """ Execute the UPDATE query"""
        pool = get_pool()
        conn = pool.getconn()
        cur = conn.cursor()

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
        cur.close()
        pool.putconn(conn)
