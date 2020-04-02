"""
Types
=====

Lyra's internal representation of Python types.

:Author: Caterina Urban
"""

import ast
from abc import ABCMeta, abstractmethod
from typing import List


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


class SequenceLyraType(LyraType, metaclass=ABCMeta):
    """Sequence type representation."""
    pass


class StringLyraType(SequenceLyraType):
    """String type representation."""

    def __repr__(self):
        return "string"


class ContainerLyraType(LyraType, metaclass=ABCMeta):
    """Container type representation."""
    pass


class ListLyraType(SequenceLyraType, ContainerLyraType):
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


class TupleLyraType(SequenceLyraType, ContainerLyraType):
    """Tuple type representation."""
    # TODO: maybe support tuples of variable length
    # To specify a variable-length tuple of homogeneous type, use literal ellipsis,
    # e.g. Tuple[int, ...].
    # A plain Tuple is equivalent to Tuple[Any, ...]

    def __init__(self, typs: List[LyraType]):
        """Tuple type creation.

        :param typs: types of the tuple elements (can be different)
        """
        self._typs = typs

    @property
    def typs(self):
        """Types of the tuple elements."""
        return self._typs

    def __repr__(self):
        if len(self.typs) == 0:    # empty tuple
            str_types = ["()"]      # -> Tuple[()]  (see https://www.python.org/dev/peps/pep-0484/)
        else:
            str_types = map(repr, self.typs)
        return "Tuple[" + ', '.join(str_types) + "]"


class SetLyraType(ContainerLyraType):
    """Set type representation."""

    def __init__(self, typ: LyraType):
        """Set type creation.

        :param typ: type of the set elements
        """
        self._typ = typ

    @property
    def typ(self):
        """Type of the set elements."""
        return self._typ

    def __repr__(self):
        return f"Set[{repr(self.typ)}]"


class DictLyraType(ContainerLyraType):
    """Dictionary type representation."""

    def __init__(self, key_typ: LyraType, val_typ: LyraType):
        """Dictionary type creation.

        :param key_typ: type of the dictionary keys
        :param val_typ: type of the dictionary values
        """
        self._key_typ = key_typ
        self._val_typ = val_typ

    @property
    def key_typ(self):
        """Type of the dictionary keys."""
        return self._key_typ

    @property
    def val_typ(self):
        """Type of the dictionary values."""
        return self._val_typ

    def __repr__(self):
        return f"Dict[{repr(self.key_typ)}, {repr(self.val_typ)}]"


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
        elif annotation.value.id == 'Set':
            value = resolve_type_annotation(annotation.slice.value)     # element type
            return SetLyraType(value)
        elif annotation.value.id == 'Tuple':
            # element types
            values = [resolve_type_annotation(v) for v in annotation.slice.value.elts]
            return TupleLyraType(values)

    if isinstance(annotation, ast.NameConstant):
        return annotation.value

    raise NotImplementedError(f"Type annotation {annotation} is not yet supported!")
