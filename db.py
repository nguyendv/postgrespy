"""
Version: 0.4
Step-by-step usage for this module:
- (Optional) Define POSTGRES_POOL_MIN_CONN, POSTGRES_POOL_MAX_CONN, 
POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
in environment file then source it. Otherwise, you need to supply then in `get_pool`
- get a pool from `pool = get_pool()`)
- from the pool, get the a connection `conn = pool.getconn()`
- from te connection, get the cursor `cur = conn.cursor()`
- working with the database through the cursor
- Don't forget to commit the connection (`conn.commit()`) and release it `pool.putconn(conn)`
"""

import os
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from jinja2 import Template


_pool = None


def get_pool(minconn=None, maxconn=None, database=None, user=None, password=None, host=None, port=None):
    """ `db.py` assumes that you use only one Postgresql database server for your application.
    If you need more than one, modifying this module is necessary.

    !IMPORTANT: if this function is never called, _pool is None, so others may not work.
    My intent is to force users call this function explicitly.
    """
    global _pool
    if _pool is None:
        if minconn is None:
            minconn = os.environ['POSTGRES_POOL_MIN_CONN']
        if maxconn is None:
            maxconn = os.environ['POSTGRES_POOL_MAX_CONN']
        if database is None:
            database = os.environ['POSTGRES_USER']
        if user is None:
            user = os.environ['POSTGRES_USER']
        if password is None:
            password = os.environ['POSTGRES_PASSWORD']
        if host is None:
            host = os.environ['POSTGRES_HOST']
        if port is None:
            port = os.environ['POSTGRES_PORT']
        _pool = ThreadedConnectionPool(minconn=minconn, maxconn=maxconn, database=database,
                                       user=user, password=password,
                                       host=host, port=port
                                       )
    return _pool


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

        See test.py for example.
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
        pool = get_pool()
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
        pool = get_pool()
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
        pool = get_pool()
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
