"""
Interval Lattice
================

:Authors: Caterina Urban and Simon Wehrli
"""

from math import inf

from lyra.abstract_domains.lattice import BottomMixin, ArithmeticMixin, BooleanMixin, SequenceMixin
from lyra.core.expressions import Literal
from lyra.core.types import BooleanLyraType, IntegerLyraType, FloatLyraType
from lyra.core.utils import copy_docstring


class IntervalLattice(BottomMixin, ArithmeticMixin, BooleanMixin, SequenceMixin):
    """Interval lattice. The bottom interval represents an empty set.

    .. image:: _static/interval.jpg

    The default abstraction is the unbounded interval ``[-oo, +oo]``.

    .. document private methods
    .. automethod:: IntervalLattice._less_equal
    .. automethod:: IntervalLattice._meet
    .. automethod:: IntervalLattice._join
    .. automethod:: IntervalLattice._widening
    .. automethod:: IntervalLattice._neg
    .. automethod:: IntervalLattice._add
    .. automethod:: IntervalLattice._sub
    .. automethod:: IntervalLattice._mult
    .. automethod:: IntervalLattice._concat
    """

    def __init__(self, lower=-inf, upper=inf):
        super().__init__()
        if lower <= upper and lower != inf and upper != -inf:      # the interval is not empty
            self._lower = lower
            self._upper = upper
        else:                   # the interval is empty
            self.bottom()

    @classmethod
    def from_literal(cls, literal: Literal) -> 'IntervalLattice':
        if isinstance(literal.typ, BooleanLyraType):
            if literal.val == "True":
                return cls().true()
            assert literal.val == "False"
            return cls().false()
        elif isinstance(literal.typ, IntegerLyraType):
            value = int(literal.val)
            return cls(value, value)
        elif isinstance(literal.typ, FloatLyraType):
            value = float(literal.val)
            return cls(value, value)
        return cls()

    def gamma(self, bound: int):
        """Concretization.

        :return: the concretization of the current interval as a list of strings
        """
        result = list()
        if self.lower != -inf and self.upper != inf:
            lower = int(self.lower)
            upper = int(self.upper + 1)
            for value in range(lower, upper):
                result.append(str(value))
        elif self.lower != -inf:
            lower = int(self.lower)
            upper = int(self.lower + bound)
            for value in range(lower, upper):
                result.append(str(value))
            result.append('_')
        elif self.upper != inf:
            lower = int(self.upper - bound)
            upper = int(self.upper + 1)
            result.append('_')
            for value in range(lower, upper):
                result.append(str(value))
        else:
            result.append('_')
        return result

    @property
    def lower(self):
        """Current lower bound.

        :return: the current lower bound if the interval is not empty, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        return self._lower

    @property
    def upper(self):
        """Current upper bound.

        :return: the current upper bound if the interval is not empty, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        return self._upper

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return f"[{self.lower}, {self.upper}]"

    @copy_docstring(BottomMixin.top)
    def top(self) -> 'IntervalLattice':
        """The top lattice element is ``[-oo,+oo]``."""
        self._replace(type(self)())
        return self

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        return self.lower == -inf and self.upper == inf

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'IntervalLattice') -> bool:
        """``[a, b] ⊑ [c, d]`` if and only if ``c <= a`` and ``b <= d``."""
        return other.lower <= self.lower and self.upper <= other.upper

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] ⊔ [c, d] = [min(a,c), max(b,d)]``."""
        lower = min(self.lower, other.lower)
        upper = max(self.upper, other.upper)
        return self._replace(type(self)(lower, upper))

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] ⊓ [c, d] = [max(a,c), min(b,d)]``."""
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower <= upper:
            return self._replace(type(self)(lower, upper))
        return self.bottom()

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] ▽ [c, d] = [(c < a ? -oo : a), (b < d ? +oo : b)]``."""
        lower = self.lower
        upper = self.upper
        if other.lower < self.lower:
            lower = -inf
        if self.upper < other.upper:
            upper = inf
        return self._replace(type(self)(lower, upper))

    # arithmetic operations

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'IntervalLattice':
        """``- [a, b] = [-b, -a]``."""
        lower = 0 - self.upper
        upper = 0 - self.lower
        return self._replace(type(self)(lower, upper))

    @copy_docstring(ArithmeticMixin._add)
    def _add(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] + [c, d] = [a + c, b + d]``."""
        lower = 0 + self.lower + other.lower
        upper = 0 + self.upper + other.upper
        return self._replace(type(self)(lower, upper))

    @copy_docstring(ArithmeticMixin._sub)
    def _sub(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] - [c, d] = [a - d, b - c]``."""
        lower = 0 + self.lower - other.upper
        upper = 0 + self.upper - other.lower
        return self._replace(type(self)(lower, upper))

    @copy_docstring(ArithmeticMixin._mult)
    def _mult(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] * [c, d] = [min(a*c, a*d, b*c, b*d), max(a*c, a*d, b*c, b*d)]``."""
        ac = 0 if self.lower == 0 or other.lower == 0 else 1 * self.lower * other.lower
        ad = 0 if self.lower == 0 or other.upper == 0 else 1 * self.lower * other.upper
        bc = 0 if self.upper == 0 or other.lower == 0 else 1 * self.upper * other.lower
        bd = 0 if self.upper == 0 or other.upper == 0 else 1 * self.upper * other.upper
        lower = min(ac, ad, bc, bd)
        upper = max(ac, ad, bc, bd)
        return self._replace(type(self)(lower, upper))

    @copy_docstring(ArithmeticMixin._div)
    def _div(self, other: 'IntervalLattice') -> 'IntervalLattice':
        return self._replace(type(self)())

    def _mod(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        return self._replace(type(self)())

    # boolean operations

    @copy_docstring(BooleanMixin.false)
    def false(self) -> 'IntervalLattice':
        """The false lattice element is ``[0,0]``."""
        self._replace(type(self)(0, 0))
        return self

    @copy_docstring(BooleanMixin.true)
    def true(self) -> 'IntervalLattice':
        """The true lattice element is ``[1,1]``."""
        self._replace(type(self)(1, 1))
        return self

    @copy_docstring(BooleanMixin.maybe)
    def maybe(self) -> 'IntervalLattice':
        """The maybe lattice element is ``[0,1]``."""
        self._replace(type(self)(0, 1))
        return self

    @copy_docstring(BooleanMixin.is_false)
    def is_false(self) -> bool:
        return self.lower == 0 and self.upper == 0

    @copy_docstring(BooleanMixin.is_true)
    def is_true(self) -> bool:
        return self.lower == 1 and self.upper == 1

    @copy_docstring(BooleanMixin.is_maybe)
    def is_maybe(self) -> bool:
        return self.lower == 0 and self.upper == 1

    # string operations

    @copy_docstring(SequenceMixin._concat)
    def _concat(self, other: 'IntervalLattice'):
        return self.join(other)
