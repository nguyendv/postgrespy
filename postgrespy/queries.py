from postgrespy.fields import BaseField, IntegerField
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
        if row is None:
            return None
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
    def __init__(self, model_cls, where: str=None):
        super().__init__(model_cls)
        self.stmt = 'SELECT ' + ','.join(self.fields) + \
            ' FROM ' + model_cls.Meta.table
        if where is not None:
            self.stmt = self.stmt + ' WHERE ' + where


class Join(Query):
    def __init__(self, model_cls_0, join_type_0: str, model_cls_1, on_clause_0: str, join_type_1=None, model_cls_2=None, on_clause_1=None):
        """ Join query for (upto 3) tables"""
        self.conn, self.cur = get_conn_cur()

        self.model_cls_0 = model_cls_0

        table_name_0 = model_cls_0.Meta.table
        self.fields_0 = [f for f in dir(model_cls_0) if not f.startswith(
            '__') and issubclass(type(getattr(model_cls_0, f)), BaseField)]
        # Add id to the list of fields
        self.fields_0 += ['id']

        self.model_cls_1 = model_cls_1
        table_name_1 = model_cls_1.Meta.table
        self.fields_1 = [f for f in dir(model_cls_1) if not f.startswith(
            '__') and issubclass(type(getattr(model_cls_1, f)), BaseField)]
        # Add id to the list of fields
        self.fields_1 += ['id']

        if model_cls_2 is not None:
            self.model_cls_2 = model_cls_2
            table_name_2 = model_cls_2.Meta.table
            self.fields_2 = [f for f in dir(model_cls_2) if not f.startswith('__')
                             and issubclass(type(getattr(model_cls_2, f)), BaseField)]
            self.fields_2 += ['id']
        else:
            self.model_cls_2 = None
            self.fields_2 = []

        self.stmt = 'SELECT ' + \
            ','.join([table_name_0 + '.' + f for f in self.fields_0] +
                     [table_name_1 + '.' + f for f in self.fields_1] +
                     [table_name_2 + '.' + f for f in self.fields_2]) + \
            ' FROM ' + table_name_0 + \
            ' ' + join_type_0 + ' ' + table_name_1
        if on_clause_0 is not None:
            self.stmt = self.stmt + ' ON ' + on_clause_0
        if model_cls_2 is not None:
            self.stmt += ' ' + join_type_1 + ' ' + table_name_2
            self.stmt += ' ON ' + on_clause_1

    def fetchone(self):
        row = self.cur.fetchone()
        if row is None:
            return None
        ret_0 = self.model_cls_0()
        ret_1 = self.model_cls_1()

        for i, f in enumerate(self.fields_0):
            setattr(ret_0, f, row[i])

        len_0 = len(self.fields_0)
        for i, f in enumerate(self.fields_1):
            setattr(ret_1, f, row[i + len_0])

        if self.model_cls_2 is None:
            return ret_0, ret_1
        else:
            ret_2 = self.model_cls_2()
            len_1 = len(self.fields_1)
            for i, f in enumerate(self.fields_2):
                setattr(ret_2, f, row[i + len_0 + len_1])
            return ret_0, ret_1, ret_2

    def fetchall(self):
        rows = self.cur.fetchall()
        ret = []
        for row in rows:
            r_0 = self.model_cls_0()
            r_1 = self.model_cls_1()

            for i, f in enumerate(self.fields_0):
                setattr(r_0, f, row[i])

            len_0 = len(self.fields_0)
            for i, f in enumerate(self.fields_1):
                setattr(r_1, f, row[i + len_0])

            if self.model_cls_2 is None:
                ret.append((r_0, r_1))
            else:
                r_2 = self.model_cls_2()
                len_1 = len(self.fields_1)
                for i, f in enumerate(self.fields_2):
                    setattr(r_2, f, row[i + len_0 + len_1])
                ret.append((r_0, r_1, r_2))
        return ret
