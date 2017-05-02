

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
