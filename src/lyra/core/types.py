import ast
from abc import ABCMeta, abstractmethod


class LyraType(metaclass=ABCMeta):
    """Type representation."""

    def __eq__(self, other: 'LyraType'):
        return isinstance(other, self.__class__) and repr(self) == repr(other)

    def __ne__(self, other: 'LyraType'):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))

    @abstractmethod
    def __repr__(self):
        """Unambiguous string representation of the type.

        :return: unambiguous string representation

        """


class BooleanLyraType(LyraType):
    """Boolean type representation."""

    def __repr__(self):
        return "bool"


class IntegerLyraType(LyraType):
    """Integer type representation."""

    def __repr__(self):
        return "int"


class StringLyraType(LyraType):
    """String type representation."""

    def __repr__(self):
        return "string"


class ListLyraType(LyraType):
    """List type representation."""

    def __init__(self, typ: LyraType):
        """List type creation.

        :param typ: type of the list element
        """
        self._typ = typ

    @property
    def typ(self):
        return self._typ

    def __repr__(self):
        return f"List[{repr(self.typ)}]"


def resolve_type_annotation(annotation):
    """Type annotation resolution."""

    if isinstance(annotation, ast.Name):
        if annotation.id == 'bool':
            return BooleanLyraType()
        elif annotation.id == 'int':
            return IntegerLyraType()
        elif annotation.id == 'str':
            return StringLyraType()

    if isinstance(annotation, ast.Subscript):
        pass

    raise ValueError(f"Type annotation {annotation} is invalid!")