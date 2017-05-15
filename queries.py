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


class Join(Query):
    def __init__(self, model_cls_left, join_type: str, model_cls_right, on_clause: str):
        self.conn, self.cur = get_conn_cur()

        self.model_cls_left = model_cls_left
        self.model_cls_right = model_cls_right

        table_name_left = model_cls_left.Meta.table
        self.fields_left = [f for f in dir(model_cls_left) if not f.startswith(
            '__') and issubclass(type(getattr(model_cls_left, f)), BaseField)]
        # Add id to the list of fields
        self.fields_left += ['id']

        table_name_right = model_cls_right.Meta.table
        self.fields_right = [f for f in dir(model_cls_right) if not f.startswith(
            '__') and issubclass(type(getattr(model_cls_right, f)), BaseField)]
        # Add id to the list of fields
        self.fields_right += ['id']

        self.stmt = 'SELECT ' + \
            ','.join([table_name_left + '.' + f for f in self.fields_left] +
                     [table_name_right + '.' + f for f in self.fields_right]) + \
            ' FROM ' + model_cls_left.Meta.table + \
            ' ' + join_type + ' ' + model_cls_right.Meta.table
        if on_clause is not None:
            self.stmt = self.stmt + ' ON ' + on_clause

        print('Join statement: ', self.stmt)

    def fetchone(self):
        row = self.cur.fetchone()
        ret_left = self.model_cls_left()
        ret_right = self.model_cls_right()

        for i, f in enumerate(self.fields_left):
            setattr(ret_left, f, row[i])

        left_len = len(self.fields_left)
        for i, f in enumerate(self.fields_right):
            setattr(ret_right, f, row[i + left_len])

        return ret_left, ret_right

    def fetchall(self):
        rows = self.cur.fetchall()
        ret = []
        for row in rows:
            r_left = self.model_cls_left()
            r_right = self.model_cls_right()

            for i, f in enumerate(self.fields_left):
                print(f, row[i])
                setattr(r_left, f, row[i])

            left_len = len(self.fields_left)
            for i, f in enumerate(self.fields_right):
                print(f, row[i + left_len])
                setattr(r_right, f, row[i + left_len])

            ret.append((r_left, r_right,))
        return ret
