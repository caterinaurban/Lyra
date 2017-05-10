from frontend.context import Context


class Class(Context):
    def __init__(self, name, parent_context=None):
        super().__init__(parent_context)
        self.name = name


class Instance:
    def __init__(self, cls):
        self.cls = cls
