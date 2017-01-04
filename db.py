"""
Version: 0.1
"""

import os
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from urllib import parse
from jinja2 import Template


parse.uses_netloc.append('postgres')
url = parse.urlparse(os.environ['DATABASE_URL'])

pool = ThreadedConnectionPool(minconn=os.environ['PG_POOL_MIN_CONN'],
                              maxconn=os.environ['PG_POOL_MAX_CONN'],
                              database=url.path[1:],
                              user=url.username,
                              password=url.password,
                              host=url.hostname,
                              port=url.port
                              )


class SqlModel:
    """
    Base class for SqlModel
    Currently, the module supports Postgresql only.

    IMPORTANT!: To use this base class, children *must*:
        - choose an 'id serial' as primary key
        - define a `_table_` class attribute
        - define a tupe `_cols_` class attribute.
        Do not include `id` in `_cols_`.
        Remember every child has a implicit `id` row.
    """

    def __init__(self, id=None, **kwargs):
        self.id = id
        for col in self._cols_:
            setattr(self, col, kwargs.get(col))

        if self.id is not None:
            self._load()

    def save(self):
        """
        Insert if id is None.
        Update if otherwise
        IMPORTANT: this is a 'dumb' method. You need to check for
        any constraint or handle exception before/after calling me.
        and DON't add new attributes after an object is created.
        """
        conn = pool.getconn()
        cur = conn.cursor()

        non_id_vals = tuple(self.__dict__[col] for col in self._cols_)

        if self.id is None:
            # Insert the row
            template = Template('INSERT INTO {{table}}\n'
                                '( {{cols}} )\n'
                                'VALUES ( {{placeholders}} )\n'
                                'RETURNING id')

            stmt = template.render(table=self._table_,
                                   cols=','.join(self._cols_),
                                   placeholders=','.join('%s'
                                                         for c in self._cols_)
                                   )
            try:
                cur.execute(stmt, non_id_vals)
                self.id = cur.fetchone()[0]
                conn.commit()
            except psycopg2.DatabaseError as e:
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
        else:
            # Update the row
            template = Template('UPDATE {{table}}\n'
                                'SET {{ cols }} \n'
                                'WHERE id = %s')
            stmt = template.render(table=self._table_,
                                   cols=','.join(
                                       c + '=%s' for c in self._cols_))
            cur.execute(stmt, non_id_vals + (self.id,))
            conn.commit()
        cur.close()
        pool.putconn(conn)

    def delete(self):
        """
        Delete the row from database.
        """
        conn = pool.getconn()
        cur = conn.cursor()
        template = Template('DELETE FROM {{table}}\n'
                            'WHERE id = %s')
        stmt = template.render(table=self._table_)
        cur.execute(stmt, (self.id,))
        self.id = None
        for col in self._cols_:
            setattr(self, col, None)
        conn.commit()
        cur.close()
        pool.putconn(conn)

    def _load(self):
        """
        Load the row from database
        Required id is not None
        """
        assert self.id is not None
        conn = pool.getconn()
        cur = conn.cursor()
        template = Template('SELECT {{cols}}\n'
                            'FROM {{table}}\n'
                            'WHERE id=%s\n'
                            'LIMIT 1')
        stmt = template.render(table=self._table_, cols=','.join(self._cols_))
        cur.execute(stmt, (self.id,))
        row = cur.fetchone()
        try:
            i = 0
            for col in self._cols_:
                setattr(self, col, row[i])
                i = i + 1
        except TypeError as e:
            # cannot access row[i]
            if str(e) == '\'NoneType\' object is not subscriptable':
                self.id = None
                for col in self._cols_:
                    setattr(self, col, None)
            else:
                raise NotImplementedError('New error. Need to check')

        cur.close()
        pool.putconn(conn)


class UniqueViolatedError(Exception):
    """Exception rasied for unique constrain violated
    """
    pass
