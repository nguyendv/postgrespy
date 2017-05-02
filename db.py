"""
Version: 0.5
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
from psycopg2.pool import ThreadedConnectionPool


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


class UniqueViolatedError(Exception):
    """Exception rasied for unique constrain violated
    """
    pass
