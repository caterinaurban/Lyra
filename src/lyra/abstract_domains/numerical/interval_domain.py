"""
Interval Abstract Domain
========================

Non-relational abstract domain to be used for **numerical analysis**.
The set of possible numerical values of a program variable in a program state
is represented as an interval.

:Authors: Caterina Urban and Simon Wehrli
"""
from collections import defaultdict
from copy import deepcopy
from math import inf

from lyra.abstract_domains.basis import Basis
from lyra.abstract_domains.lattice import BottomMixin, ArithmeticMixin, BooleanMixin
from lyra.abstract_domains.state import State
from lyra.core.expressions import *

from lyra.core.utils import copy_docstring
from lyra.core.types import BooleanLyraType, IntegerLyraType, FloatLyraType


class IntervalLattice(BottomMixin, ArithmeticMixin, BooleanMixin):
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
    """

    def __init__(self, lower=-inf, upper=inf):
        super().__init__()
        if lower <= upper and lower != inf and upper !=-inf:      # the interval is not empty
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


class IntervalState(Basis):
    """Interval analysis state. An element of the interval abstract domain.

    Map from each program variable to the interval representing its value.
    The value of all program variables is represented by the unbounded interval by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: IntervalState._assign
    .. automethod:: IntervalState._assume
    .. automethod:: IntervalState._output
    .. automethod:: IntervalState._substitute

    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        """Map each program variable to the interval representing its value.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: IntervalLattice)
        super().__init__(variables, lattices, precursory=precursory)

    @copy_docstring(Basis._assume)
    def _assume(self, condition: Expression) -> 'IntervalState':
        normal = NegationFreeNormalExpression().visit(condition)
        if isinstance(normal, VariableIdentifier) and isinstance(normal.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(normal, self, dict())
            true = self.lattices[normal.typ](**self.arguments[normal.typ]).true()
            return self._refinement.visit(normal, evaluation, true, self)
        elif isinstance(normal, UnaryBooleanOperation):
            if normal.operator == UnaryBooleanOperation.Operator.Neg:
                expression = normal.expression
                if isinstance(expression, VariableIdentifier):
                    typ = expression.typ
                    if isinstance(expression.typ, BooleanLyraType):
                        evaluation = self._evaluation.visit(normal, self, dict())
                        false = self.lattices[typ](**self.arguments[typ]).false()
                        return self._refinement.visit(expression, evaluation, false, self)
        elif isinstance(normal, BinaryBooleanOperation):
            return self._assume_binarybooleanoperation(normal)
        elif isinstance(normal, BinaryComparisonOperation):
            if normal.operator == BinaryComparisonOperation.Operator.Is:
                error = f"Assumption of a comparison with {normal.operator} is unsupported!"
                raise ValueError(error)
            elif normal.operator == BinaryComparisonOperation.Operator.IsNot:
                error = f"Assumption of a comparison with {normal.operator} is unsupported!"
                raise ValueError(error)
            elif normal.operator == BinaryComparisonOperation.Operator.In:
                if isinstance(normal.right, Range):
                    typ = BooleanLyraType()
                    left = normal.left
                    lower_operator = BinaryComparisonOperation.Operator.GtE
                    lower_right = normal.right.start
                    lower = BinaryComparisonOperation(typ, left, lower_operator, lower_right)
                    upper_operator = BinaryComparisonOperation.Operator.Lt
                    upper_right = normal.right.stop
                    upper = BinaryComparisonOperation(typ, left, upper_operator, upper_right)
                    right = deepcopy(self)._assume(upper)
                    return self._assume(lower).meet(right)
            elif normal.operator == BinaryComparisonOperation.Operator.NotIn:
                if isinstance(normal.right, Range):
                    typ = BooleanLyraType()
                    left = normal.left
                    lower_operator = BinaryComparisonOperation.Operator.Lt
                    lower_right = normal.right.start
                    lower = BinaryComparisonOperation(typ, left, lower_operator, lower_right)
                    upper_operator = BinaryComparisonOperation.Operator.GtE
                    upper_right = normal.right.stop
                    upper = BinaryComparisonOperation(typ, left, upper_operator, upper_right)
                    right = deepcopy(self)._assume(upper)
                    return self._assume(lower).join(right)
            evaluation = self._evaluation.visit(normal.left, self, dict())
            nonpositive = self.lattices[normal.typ](upper=0)
            return self._refinement.visit(normal.left, evaluation, nonpositive, self)
        error = f"Assumption of a {normal.__class__.__name__} expression is unsupported!"
        raise ValueError(error)

    # expression evaluation

    class ExpressionEvaluation(Basis.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the interval lattice."""

        @copy_docstring(Basis.ExpressionEvaluation.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation    # nothing to be done
            evaluation[expr] = state.lattices[expr.typ].from_literal(expr)
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances
