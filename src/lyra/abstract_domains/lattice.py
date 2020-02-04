"""
Lattice
=======

Interface of a lattice. Lattice elements support lattice operations.

:Author: Caterina Urban
"""

from abc import ABCMeta, abstractmethod
from enum import Enum
from functools import reduce
from typing import List

from lyra.core.expressions import VariableIdentifier
from lyra.core.utils import copy_docstring


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
        :return: whether the current lattice element is less than or equal to the other element

        """

    def less_equal(self, other: 'Lattice') -> bool:
        """Partial order between lattice elements.

        :param other: other lattice element
        :return: whether the current lattice element is less than or equal to the other element

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
        :return: current lattice element modified to be the least upper bound

        """

    def join(self, other: 'Lattice') -> 'Lattice':
        """Least upper bound between lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the least upper bound

        """
        if self.is_bottom() or other.is_top():
            return self._replace(other)
        elif other.is_bottom() or self.is_top():
            return self
        else:
            return self._join(other)

    def big_join(self, elements: List['Lattice']) -> 'Lattice':
        """Least upper bound between multiple lattice elements.

        :param elements: lattice elements to compute the least upper bound of
        :return: current lattice element modified to be the least upper bound

        """
        return reduce(lambda s1, s2: s1.join(s2), elements, self.bottom())

    @abstractmethod
    def _meet(self, other: 'Lattice'):
        """Greatest lower bound between default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the greatest lower bound

        """

    def meet(self, other: 'Lattice'):
        """Greatest lower bound between lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the greatest lower bound

        """
        if self.is_top() or other.is_bottom():
            return self._replace(other)
        elif other.is_top() or self.is_bottom():
            return self
        else:
            return self._meet(other)

    def big_meet(self, elements: List['Lattice']) -> 'Lattice':
        """Greatest lower bound between multiple lattice elements.

        :param elements: lattice elements to compute the greatest lower bound of
        :return: current lattice element modified to be the least upper bound

        """
        return reduce(lambda s1, s2: s1.meet(s2), elements, self.top())

    @abstractmethod
    def _widening(self, other: 'Lattice'):
        """Widening between default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the widening

        """

    def widening(self, other: 'Lattice'):
        """Widening between lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the widening

        """
        if self.is_bottom() or other.is_top():
            return self._replace(other)
        elif other.is_bottom() or self.is_top():
            return self
        else:
            return self._widening(other)

    def _replace(self, other: 'Lattice') -> 'Lattice':
        """Replace this instance with another lattice element.

        :param other: other lattice element
        :return: current lattice element updated to be equal to other

        """
        self.__dict__.update(other.__dict__)
        return self


class KindMixin(Lattice, metaclass=ABCMeta):
    """Mixin to add an explicit distinction between bottom, default, and top lattice elements."""

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
    """Mixin to add a predefined bottom element to a lattice.

    .. warning::
        Subclasses are expected to provide consistent method implementations
        that check for the eventuality of ``is_bottom()`` being true.
    """

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        self.kind = KindMixin.Kind.BOTTOM
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return self.kind == KindMixin.Kind.BOTTOM


class TopMixin(KindMixin, metaclass=ABCMeta):
    """Mixin to add a predefined top element to another lattice.

    .. warning::
        Subclasses are expected to provide consistent method implementations
        that check for the eventuality of ``is_top()`` being true.
    """

    @copy_docstring(Lattice.top)
    def top(self):
        self.kind = KindMixin.Kind.TOP
        return self

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self.kind == KindMixin.Kind.TOP


class BoundedLattice(KindMixin, metaclass=ABCMeta):
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


class ArithmeticMixin(Lattice, metaclass=ABCMeta):
    """Mixin to add arithmetic operations to a lattice."""

    @abstractmethod
    def _neg(self) -> 'ArithmeticMixin':
        """Negation of a default lattice elements.

        :return: current lattice element modified to be its negation

        """

    def neg(self) -> 'ArithmeticMixin':
        """Negation of a lattice elements.

        :return: current lattice element modified to be its negation

        """
        if self.is_bottom():
            return self
        else:
            return self._neg()

    @abstractmethod
    def _add(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Addition between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the sum

        """

    def add(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Addition between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the sum

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self._replace(other)
        else:
            return self._add(other)

    @abstractmethod
    def _sub(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Subtraction between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the difference

        """

    def sub(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Subtraction between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the difference

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self._replace(other)
        else:
            return self._sub(other)

    @abstractmethod
    def _mult(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Multiplication between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the product

        """

    def mult(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Multiplication between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the product

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self._replace(other)
        else:
            return self._mult(other)

    @abstractmethod
    def _div(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Division between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the division

        """

    def div(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Division between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the division

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self._replace(other)
        else:
            return self._div(other)

    @abstractmethod
    def _mod(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Modulo between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the reminder

        """

    def mod(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Modulo between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the reminder

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self._replace(other)
        else:
            return self._mod(other)


class BooleanMixin(Lattice, metaclass=ABCMeta):
    """Mixin to add boolean operations to a lattice."""

    @abstractmethod
    def false(self) -> 'BooleanMixin':
        """False lattice element.

        :return: current lattice element modified to be the false lattice element

        """

    @abstractmethod
    def true(self) -> 'BooleanMixin':
        """True lattice element.

        :return: current lattice element modified to be the true lattice element

        """

    @abstractmethod
    def maybe(self) -> 'BooleanMixin':
        """Maybe lattice element.

        :return: current lattice element modified to be the maybe lattice element

        """

    @abstractmethod
    def is_false(self) -> bool:
        """Test whether the lattice element is false.

        :return: whether the lattice element is false

        """

    @abstractmethod
    def is_true(self) -> bool:
        """Test whether the lattice element is true.

        :return: whether the lattice element is true

        """

    @abstractmethod
    def is_maybe(self) -> bool:
        """Test whether the lattice element is maybe.

        :return: whether the lattice element is maybe

        """

    def _compl(self) -> 'BooleanMixin':
        """Complement of a default lattice elements.

        :return: current lattice element modified to be its complement

        """
        if self.is_false():
            return self.true()
        elif self.is_true():
            return self.false()
        return self

    def compl(self) -> 'BooleanMixin':
        """Complement of a lattice elements.

        :return: current lattice element modified to be its complement

        """
        if self.is_bottom():
            return self
        else:
            return self._compl()

    def _conj(self, other: 'BooleanMixin') -> 'BooleanMixin':
        """Conjunction between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the conjunction

        """
        if self.is_false() or other.is_false():
            return self.false()
        elif self.is_maybe() or other.is_maybe():
            return self.maybe()
        return self.true()

    def conj(self, other: 'BooleanMixin') -> 'BooleanMixin':
        """Conjunction between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the conjunction

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self._replace(other)
        else:
            return self._conj(other)

    def _disj(self, other: 'BooleanMixin') -> 'BooleanMixin':
        """Disjunction between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the disjunction

        """
        if self.is_true() or other.is_true():
            return self.true()
        elif self.is_maybe() or other.is_maybe():
            return self.maybe()
        return self.false()

    def disj(self, other: 'BooleanMixin') -> 'BooleanMixin':
        """Disjunction between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the disjunction

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self._replace(other)
        else:
            return self._disj(other)


class SequenceMixin(Lattice, metaclass=ABCMeta):
    """Mixin to add sequence operations to a lattice."""

    @abstractmethod
    def _concat(self, other: 'SequenceMixin') -> 'SequenceMixin':
        """Concatenation between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the concatenation

        """

    def concat(self, other: 'SequenceMixin') -> 'SequenceMixin':
        """Concatenation between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the concatenation

        """
        if self.is_bottom():        # self is the empty sequence
            return self._replace(other)
        elif other.is_bottom():     # other is the empty sequence
            return self
        else:
            return self._concat(other)


class EnvironmentMixin(Lattice, metaclass=ABCMeta):
    """Mixin to add environment modification operations to another lattice."""

    @abstractmethod
    def unify(self, other: 'EnvironmentMixin') -> 'EnvironmentMixin':
        """Unification between (environments of) lattice elements.

        :param other: other lattice element
        :return: current lattice element updated to have the least common environment
        """

    def less_equal(self, other: 'EnvironmentMixin') -> bool:
        if self.is_bottom() or other.is_top():
            return True
        elif other.is_bottom() or self.is_top():
            return False
        else:
            return self.unify(other)._less_equal(other.unify(self))

    def join(self, other: 'EnvironmentMixin') -> 'EnvironmentMixin':
        if self.is_bottom() or other.is_top():
            return self._replace(other)
        elif other.is_bottom() or self.is_top():
            return self
        else:
            return self.unify(other)._join(other.unify(self))

    def meet(self, other: 'EnvironmentMixin') -> 'EnvironmentMixin':
        if self.is_top() or other.is_bottom():
            return self._replace(other)
        elif other.is_top() or self.is_bottom():
            return self
        else:
            return self.unify(other)._meet(other.unify(self))

    def widening(self, other: 'EnvironmentMixin') -> 'EnvironmentMixin':
        if self.is_bottom() or other.is_top():
            return self._replace(other)
        elif other.is_bottom() or self.is_top():
            return self
        else:
            return self.unify(other)._widening(other.unify(self))

    @abstractmethod
    def add_variable(self, variable: VariableIdentifier) -> 'EnvironmentMixin':
        """Add a variable.

        :param variable: variable to be added
        :return: current lattice modified by the variable addition
        """

    @abstractmethod
    def remove_variable(self, variable: VariableIdentifier) -> 'EnvironmentMixin':
        """Remove a variable.

        :param variable: variable to be removed
        :return: current lattice modified by the variable removal
        """
