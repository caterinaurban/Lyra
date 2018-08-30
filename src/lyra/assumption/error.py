from abc import ABCMeta


class CheckerError(metaclass=ABCMeta):

    def __init__(self, message: str):
        self._message = message

    @property
    def message(self):
        return self._message

    def __repr__(self):
        return "{}".format(self.message)


class RelationalError(CheckerError):
    def __init__(self, message: str):
        super().__init__(message)


class DependencyError(CheckerError):
    def __init__(self, source_line: int):
        self.source_line = source_line
        super().__init__('')
