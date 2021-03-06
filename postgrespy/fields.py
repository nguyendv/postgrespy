from datetime import datetime

import psycopg2
import psycopg2.extras

class BaseField:
    def __init__(self):
        pass


class TextField(BaseField, str):
    def __init__(self, value: str = None) -> None:
        super().__init__()
        self.value = value


class EnumField(BaseField, str):
    def __init__(self, value: str = None) -> None:
        super().__init__()
        self.value = value


class IntegerField(BaseField, int):
    def __init__(self, value: int = None) -> None:
        super().__init__()
        self.value = value


class BooleanField(BaseField):
    def __init__(self, value: bool= None) -> None:
        super().__init__()
        self.value = value

    def __eq__(self, val: object):
        return self.value is val


class JsonBField(BaseField, dict):
    def __init__(self, value: object = None) -> None:
        super().__init__()
        self.value = value

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, val):
        self.value[key] = val


class ArrayField(BaseField, list):
    def __init__(self, value: list = None) -> None:
        super().__init__()
        self.value = value
        self._index = 0

    def __len__(self):
        return len(self.value)

    def __getitem__(self, index):
        return self.value[index]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self.value):
            raise StopIteration
        else:
            self._index += 1
            return self.value[self._index - 1]


class DateTimeField(BaseField):
    """ Translate the datetime.datetime class into timestamp field without timezone in postgresql."""

    def __init__(self, value: datetime = None) -> None:
        super().__init__()
        self.value = value


"""Adapt Python dict as Postgres Json"""
psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)



