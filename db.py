import os
import psycopg2
from urllib import parse
from jinja2 import Template
from flask import g

parse.uses_netloc.append('postgres')
url = parse.urlparse(os.environ['DATABASE_URL'])


def get_db_connect():
    """Open a new database connection if there is none yet
    for the application app context.
    """
    # if not hasattr(g, 'db_conn'):
    #     g.db_conn = psycopg2.connect(
    #         database=url.path[1:],
    #         user=url.username,
    #         password=url.password,
    #         host=url.hostname,
    #         port=url.port
    #     )
    # return g.db_conn

    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port)


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
        cur = g.db.cursor()

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
                g.db.commit()
            except psycopg2.DatabaseError as e:
                g.db.rollback()
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
            g.db.commit()
        cur.close()

    def delete(self):
        """
        Delete the row from database.
        """
        cur = g.db.cursor()
        template = Template('DELETE FROM {{table}}\n'
                            'WHERE id = %s')
        stmt = template.render(table=self._table_)
        cur.execute(stmt, (self.id,))
        self.id = None
        for col in self._cols_:
            setattr(self, col, None)
        g.db.commit()
        cur.close()

    def _load(self):
        """
        Load the row from database
        Required id is not None
        """
        assert self.id is not None
        cur = g.db.cursor()
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


class UniqueViolatedError(Exception):
    """Exception rasied for unique constrain violated
    """
    pass
