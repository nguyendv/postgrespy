

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

    def __bool__(self):
        if self.value is None:
            return False
        return self.value

    def __eq__(self, val: bool):
        return self.value is val
