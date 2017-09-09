from datetime import datetime


class BaseField:
    def __init__(self):
        pass


class TextField(BaseField, str):
    def __init__(self, value: str = None):
        super().__init__()
        self.value = value


class EnumField(BaseField, str):
    def __init__(self, value: str = None):
        super().__init__()
        self.value = value


class IntegerField(BaseField, int):
    def __init__(self, value: int = None):
        super().__init__()
        self.value = value


class BooleanField(BaseField):
    def __init__(self, value: bool= None):
        super().__init__()
        self.value = value

    def __eq__(self, val: bool):
        return self.value is val


class JsonBField(BaseField, dict):
    def __init__(self, value: object = None):
        super().__init__()
        self.value = value

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, val):
        self.value[key] = val


class ArrayField(BaseField, list):
    def __init__(self, value: list = None):
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

    def __init__(self, value: datetime = None):
        super().__init__()
        self.value = value
