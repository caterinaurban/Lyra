from abc import ABCMeta


class CheckerError(metaclass=ABCMeta):

    def __init__(self, message: str):
        self._message = message

    @property
    def message(self):
        return self._message


class RelationalError(CheckerError):
    def __init__(self, message:str):
        super().__init__("Relation violated: {}".format(message))


class DependencyError(CheckerError):
    def __init__(self, source_line: int, message: str):
        super().__init__("Dependency error on line {}: {}".format(source_line, message))