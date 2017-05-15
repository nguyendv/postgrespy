from postgrespy.fields import BaseField
from postgrespy.db import get_conn_cur, close
from typing import Tuple


class Query:
    def __init__(self, model_cls):
        self.conn, self.cur = get_conn_cur()
        self.model_cls = model_cls
        self.fields = [f for f in dir(model_cls) if not f.startswith(
            '__') and issubclass(type(getattr(model_cls, f)), BaseField)]
        self.fields = self.fields + ['id']  # Add id to the list of fields

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        print('[queries.Query]: closing conn and cur')
        close(self.conn, self.cur)

    def execute(self, values: Tuple = None):
        self.cur.execute(self.stmt, values)

    def fetchone(self):
        row = self.cur.fetchone()
        ret = self.model_cls()
        for i, f in enumerate(self.fields):
            setattr(ret, f, row[i])
        return ret

    def fetchall(self):
        rows = self.cur.fetchall()
        ret = []
        for row in rows:
            r = self.model_cls()
            for i, f in enumerate(self.fields):
                setattr(r, f, row[i])
            ret.append(r)
        return ret


class Select(Query):
    def __init__(self, model_cls, where: str = None):
        super().__init__(model_cls)
        self.stmt = 'SELECT ' + ','.join(self.fields) + \
            ' FROM ' + model_cls.Meta.table
        if where is not None:
            self.stmt = self.stmt + ' WHERE ' + where
