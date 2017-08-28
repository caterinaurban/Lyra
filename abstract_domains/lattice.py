"""
Lattice
=======

Interface of a lattice. Lattice elements support lattice operations.
"""

from abc import ABCMeta, abstractmethod
from enum import Enum
from functools import reduce
from typing import List

from core.utils import copy_docstring


class Lattice(metaclass=ABCMeta):
    """Mutable lattice element.

    .. warning::
        Lattice operations modify the current lattice element.

        Subclasses are expected to provide consistent method implementations for
        ``bottom()``, ``is_bottom()``, ``top()`` and ``is_top()``.
    """

    def __eq__(self, other: 'Lattice'):
        return isinstance(other, self.__class__) and repr(self) == repr(other)

    def __ne__(self, other: 'Lattice'):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))

    @abstractmethod
    def __repr__(self):
        """Unambiguous string representation of the current lattice element.

        :return: unambiguous string representation

        """

    @abstractmethod
    def bottom(self):
        """Bottom lattice element.

        :return: current lattice element modified to be the bottom lattice element

        """

    @abstractmethod
    def top(self):
        """Top lattice element.

        :return: current lattice element modified to be the top lattice element

        """

    @abstractmethod
    def is_bottom(self) -> bool:
        """Test whether the lattice element is bottom.

        :return: whether the lattice element is bottom

        """

    @abstractmethod
    def is_top(self) -> bool:
        """Test whether the lattice element is top.

        :return: whether the lattice element is top

        """

    @abstractmethod
    def _less_equal(self, other: 'Lattice') -> bool:
        """Partial order between default lattice elements.

        :param other: other lattice element
        :return: whether the current lattice element is less than or equal to the other lattice element

        """

    def less_equal(self, other: 'Lattice') -> bool:
        """Partial order between lattice elements.

        :param other: other lattice element
        :return: whether the current lattice element is less than or equal to the other lattice element

        """
        if self.is_bottom() or other.is_top():
            return True
        elif other.is_bottom() or self.is_top():
            return False
        else:
            return self._less_equal(other)

    @abstractmethod
    def _join(self, other: 'Lattice') -> 'Lattice':
        """Least upper bound between default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the least upper bound of the two lattice elements

        """

    def join(self, other: 'Lattice') -> 'Lattice':
        """Least upper bound between lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the least upper bound of the two lattice elements

        """
        if self.is_bottom() or other.is_top():
            return self.replace(other)
        elif other.is_bottom() or self.is_top():
            return self
        else:
            return self._join(other)

    def big_join(self, elements: List['Lattice']) -> 'Lattice':
        """Least upper bound between multiple lattice elements.

        :param elements: lattice elements to compute the least upper bound of
        :return: current lattice element modified to be the least upper bound of the lattice elements

        """
        return reduce(lambda s1, s2: s1.join(s2), elements, self.bottom())

    @abstractmethod
    def _meet(self, other: 'Lattice'):
        """Greatest lower bound between default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the greatest lower bound of the two lattice elements

        """

    def meet(self, other: 'Lattice'):
        """Greatest lower bound between lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the greatest lower bound of the two lattice elements

        """
        if self.is_top() or other.is_bottom():
            return self.replace(other)
        elif other.is_top() or self.is_bottom():
            return self
        else:
            return self._meet(other)

    def big_meet(self, elements: List['Lattice']) -> 'Lattice':
        """Greatest lower bound between multiple lattice elements.

        :param elements: lattice elements to compute the greatest lower bound of
        :return: current lattice element modified to be the least upper bound of the lattice elements

        """
        return reduce(lambda s1, s2: s1.meet(s2), elements, self.top())

    @abstractmethod
    def _widening(self, other: 'Lattice'):
        """Widening between default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the widening of the two lattice elements

        """

    def widening(self, other: 'Lattice'):
        """Widening between lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the widening of the two lattice elements

        """
        if self.is_bottom() or other.is_top():
            return self.replace(other)
        else:
            return self._widening(other)

    def replace(self, other: 'Lattice') -> 'Lattice':
        """Replace this instance with another lattice element.

        :param other: other lattice element
        :return: current lattice element updated to be equal to other

        """
        self.__dict__.update(other.__dict__)
        return self


class KindMixin(Lattice, metaclass=ABCMeta):
    """Mixin that adds an explicit distinction between bottom, default, and top elements to a lattice."""

    class Kind(Enum):
        """Kind of a lattice element."""
        TOP = 3
        DEFAULT = 2
        BOTTOM = 1

    def __init__(self):
        """Create a default lattice element."""
        self._kind = KindMixin.Kind.DEFAULT

    @property
    def kind(self):
        """The kind of the current lattice element."""
        return self._kind

    @kind.setter
    def kind(self, kind: 'KindMixin.Kind'):
        self._kind = kind


class BottomMixin(KindMixin, metaclass=ABCMeta):
    """Mixin that adds a predefined bottom element to a lattice."""

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        self._kind = KindMixin.Kind.BOTTOM
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return self._kind == KindMixin.Kind.BOTTOM


class TopMixin(KindMixin, metaclass=ABCMeta):
    """Mixin that adds a predefined top element to another lattice."""

    @copy_docstring(Lattice.top)
    def top(self):
        self._kind = KindMixin.Kind.TOP
        return self

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self._kind == KindMixin.Kind.TOP


class BoundedLattice(TopMixin, BottomMixin, metaclass=ABCMeta):
    """Mutable lattice element, with predefined bottom and top elements.

    .. warning::
        Lattice operations modify the current lattice element.
    """

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'BoundedLattice':
        self.kind = KindMixin.Kind.BOTTOM
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'BoundedLattice':
        self.kind = KindMixin.Kind.TOP
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return self.kind == KindMixin.Kind.BOTTOM

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self.kind == KindMixin.Kind.TOP
