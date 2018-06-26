"""
Types
=====

Lyra's internal representation of Python types.

:Author: Caterina Urban
"""

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


class FloatLyraType(LyraType):
    """Float type representation."""

    def __repr__(self):
        return "float"


class StringLyraType(LyraType):
    """String type representation."""

    def __repr__(self):
        return "string"


class ListLyraType(LyraType):
    """List type representation."""

    def __init__(self, typ: LyraType):
        """List type creation.

        :param typ: type of the list elements
        """
        self._typ = typ

    @property
    def typ(self):
        """Type of the list elements."""
        return self._typ

    def __repr__(self):
        return f"List[{repr(self.typ)}]"


class DictLyraType(LyraType):
    """Dictionary type representation."""

    def __init__(self, key_type: LyraType, value_type: LyraType):
        """Dictionary type creation.

        :param key_type: type of the dictionary keys
        :param value_type: type of the dictionary values
        """
        self._key_type = key_type
        self._value_type = value_type

    @property
    def key_type(self):
        """Type of the dictionary keys."""
        return self._key_type

    @property
    def value_type(self):
        """Type of the dictionary values."""
        return self._value_type

    def __repr__(self):
        return f"Dict[{repr(self.key_type)}, {repr(self.value_type)}]"


def resolve_type_annotation(annotation):
    """Type annotation resolution."""

    if isinstance(annotation, ast.Name):
        if annotation.id == 'bool':
            return BooleanLyraType()
        elif annotation.id == 'int':
            return IntegerLyraType()
        elif annotation.id == 'float':
            return FloatLyraType()
        elif annotation.id == 'str':
            return StringLyraType()

    if isinstance(annotation, ast.Subscript):
        if annotation.value.id == 'List':
            value = resolve_type_annotation(annotation.slice.value)     # element type
            return ListLyraType(value)
        elif annotation.value.id == 'Dict':
            key = resolve_type_annotation(annotation.slice.value.elts[0])       # key type
            value = resolve_type_annotation(annotation.slice.value.elts[1])     # value type
            return DictLyraType(key, value)

    raise NotImplementedError(f"Type annotation {annotation} is not yet supported!")
