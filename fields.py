

class BaseField:
    def __init__(self):
        pass


class TextField(BaseField):
    def __init__(self, value: str = None):
        super().__init__()
        self.value = value


class EnumField(BaseField):
    def __init__(self, value: str = None):
        super().__init__()
        self.value = value


class IntegerField(BaseField):
    def __init__(self, value: int = None):
        super().__init__()
        self.value = value
