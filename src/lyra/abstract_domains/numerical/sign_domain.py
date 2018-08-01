"""
Sign Abstract Domain
====================

Non-relational abstract domain to be used for **numerical analysis**.
The set of possible values of a program variable is represented as their sign
(negative, zero, positive, ...).

:Author: Jérôme Dohrau and Caterina Urban
"""
from collections import defaultdict
from copy import deepcopy

from lyra.abstract_domains.basis import Basis
from lyra.abstract_domains.lattice import ArithmeticMixin, BooleanMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import *
from lyra.core.types import FloatLyraType

from lyra.core.utils import copy_docstring


class SignLattice(ArithmeticMixin, BooleanMixin):
    """Sign lattice.

    .. image:: _static/sign.png

    .. document private methods
    .. automethod:: SignLattice._less_equal
    .. automethod:: SignLattice._meet
    .. automethod:: SignLattice._join
    .. automethod:: SignLattice._widening
    .. automethod:: SignLattice._neg
    .. automethod:: SignLattice._add
    .. automethod:: SignLattice._sub
    .. automethod:: SignLattice._mult
    """

    def __init__(self, negative=True, zero=True, positive=True):
        super().__init__()
        self._negative = negative
        self._zero = zero
        self._positive = positive

    @classmethod
    def from_literal(cls, literal: Literal) -> 'SignLattice':
        if isinstance(literal.typ, BooleanLyraType):
            if literal.val == "True":
                return SignLattice(False, False, True)
            assert literal.val == "False"
            return SignLattice(False, True, False)
        elif isinstance(literal.typ, IntegerLyraType):
            value = int(literal.val)
            return SignLattice(value < 0, value == 0, value > 0)
        elif isinstance(literal.typ, FloatLyraType):
            value = float(literal.val)
            return SignLattice(value < 0.0, value == 0.0, value > 0.0)
        return SignLattice()

    @property
    def negative(self):
        """Current negative flag.

        :return: the current negative flag
        """
        return self._negative

    @property
    def zero(self):
        """Current zero flag.

        :return: the current zero flag
        """
        return self._zero

    @property
    def positive(self):
        """Current positive flag.

        :return: the current positive flag
        """
        return self._positive

    def is_negative(self) -> bool:
        """ Indicates whether the element is certainly negative.

        :return: ``True`` if the element is negative.
        """
        return self.negative and not self.positive and not self.zero

    def is_zero(self) -> bool:
        """ Indicates whether the element is certainly zero.

        :return: ``True`` if the element is zero.
        """
        return not self.negative and not self.positive and self.zero

    def is_positive(self) -> bool:
        """ Indicates whether the element is certainly positive.

        :return: ``True`` if the element is positive.
        """
        return not self.negative and self.positive and not self.zero

    def maybe_negative(self) -> bool:
        """ Indicates whether the element may be negative.

        :return: ``True`` if the element may be negative.
        """
        return self.negative

    def maybe_zero(self) -> bool:
        """ Indicates whether the element may be zero.

        :return: ``True`` if the element may be zero.
        """
        return self.zero

    def maybe_positive(self) -> bool:
        """ Indicates whether the element may be positive.

        :return: ``True`` if the element may be positive.
        """
        return self.positive

    def maybe_non_negative(self) -> bool:
        """ Indicates whether the element may be non-negative.

        :return: ``True`` if the element may be non-negative.
        """
        return self.zero or self.positive

    def maybe_non_zero(self) -> bool:
        """ Indicates whether the element may be non-zero.

        :return: ``True`` if the element may be non-zero.
        """
        return self.negative or self.positive

    def maybe_non_positive(self) -> bool:
        """ Indicates whether the element may be non-positive.

        :return: ``True`` if the element may be non-positive.
        """
        return self.negative or self.zero

    def __repr__(self):
        if self.is_top():
            return "⊤"
        elif self.maybe_negative() and self.maybe_zero():
            return "≤0"
        elif self.maybe_zero() and self.maybe_positive():
            return "≥0"
        elif self.maybe_negative() and self.maybe_positive():
            return "≠0"
        elif self.maybe_negative():
            return "<0"
        elif self.maybe_positive():
            return ">0"
        elif self.maybe_zero():
            return "=0"
        else:  # self.is_bottom()
            return "⊥"

    @copy_docstring(ArithmeticMixin.bottom)
    def bottom(self) -> 'SignLattice':
        return self._replace(SignLattice(False, False, False))

    @copy_docstring(ArithmeticMixin.top)
    def top(self) -> 'SignLattice':
        return self._replace(SignLattice(True, True, True))

    @copy_docstring(ArithmeticMixin.is_bottom)
    def is_bottom(self) -> bool:
        return not self.negative and not self.positive and not self.zero

    @copy_docstring(ArithmeticMixin.is_top)
    def is_top(self) -> bool:
        return self.negative and self.positive and self.zero

    @copy_docstring(ArithmeticMixin._less_equal)
    def _less_equal(self, other: 'SignLattice') -> bool:
        negative = not self.maybe_negative() or other.maybe_negative()
        zero = not self.maybe_zero() or other.maybe_zero()
        positive = not self.maybe_positive() or other.maybe_positive()
        return negative and zero and positive

    @copy_docstring(ArithmeticMixin._join)
    def _join(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative() or other.maybe_negative()
        zero = self.maybe_zero() or other.maybe_zero()
        positive = self.maybe_positive() or other.maybe_positive()
        return self._replace(SignLattice(negative, zero, positive))

    @copy_docstring(ArithmeticMixin._meet)
    def _meet(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative() and other.maybe_negative()
        zero = self.maybe_zero() and other.maybe_zero()
        positive = self.maybe_positive() and other.maybe_positive()
        return self._replace(SignLattice(negative, zero, positive))

    @copy_docstring(ArithmeticMixin._widening)
    def _widening(self, other: 'SignLattice') -> 'SignLattice':
        return self._join(other)

    # arithmetic operations

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'SignLattice':
        negative = self.maybe_positive()
        zero = self.maybe_zero()
        positive = self.maybe_negative()
        return self._replace(SignLattice(negative, zero, positive))

    def _add(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative() and not other.is_bottom()) or \
                   (self.maybe_non_negative() and other.maybe_negative())
        positive = (self.maybe_positive() and not other.is_bottom()) or \
                   (self.maybe_non_positive() and other.maybe_positive())
        zero = (self.maybe_zero() and other.maybe_zero()) or \
               (self.maybe_negative() and other.maybe_positive()) or \
               (self.maybe_positive() and other.maybe_negative())
        return self._replace(SignLattice(negative, zero, positive))

    def _sub(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative() and not other.is_bottom()) or \
                   (self.maybe_non_negative() and other.maybe_positive())
        positive = (self.maybe_positive() and not other.is_bottom()) or \
                   (self.maybe_non_positive() and other.maybe_negative())
        zero = (self.maybe_zero() and other.maybe_zero()) or \
               (self.maybe_negative() and other.maybe_negative()) or \
               (self.maybe_positive() and other.maybe_positive())
        return self._replace(SignLattice(negative, zero, positive))

    def _mult(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative() and other.maybe_positive()) or \
                   (self.maybe_positive() and other.maybe_negative())
        positive = (self.maybe_negative() and other.maybe_negative()) or \
                   (self.maybe_positive() and other.maybe_positive())
        zero = self.maybe_zero() or other.maybe_zero()
        return self._replace(SignLattice(negative, zero, positive))

    def _div(self, other: 'SignLattice') -> 'SignLattice':
        return self._replace(SignLattice())

    # boolean operations

    @copy_docstring(BooleanMixin.false)
    def false(self) -> 'SignLattice':
        """The false lattice element is ``=0``."""
        self._replace(SignLattice(False, True, False))
        return self

    @copy_docstring(BooleanMixin.true)
    def true(self) -> 'SignLattice':
        """The true lattice element is ``>0``."""
        self._replace(SignLattice(False, False, True))
        return self

    @copy_docstring(BooleanMixin.maybe)
    def maybe(self) -> 'SignLattice':
        """The maybe lattice element is ``≥0``."""
        self._replace(SignLattice(False, True, True))
        return self

    @copy_docstring(BooleanMixin.is_false)
    def is_false(self) -> bool:
        return not self.negative and self.zero and not self.positive

    @copy_docstring(BooleanMixin.is_true)
    def is_true(self) -> bool:
        return not self.negative and not self.zero and self.positive

    @copy_docstring(BooleanMixin.is_maybe)
    def is_maybe(self) -> bool:
        return not self.negative and self.zero and self.positive


class SignState(Basis):
    """Sign analysis state. An element of the sign abstract domain.

    Map from each program variable to the sign representing its value.

    .. document private methods
    .. automethod:: SignState._assign
    .. automethod:: SignState._assume
    .. automethod:: SignState._output
    .. automethod:: SignState._substitute

    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        """Map each program variable to the sign representing its value.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: SignLattice)
        super().__init__(variables, lattices, precursory=precursory)

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'SignState':
        normal = NegationFreeNormalExpression().visit(condition)
        if isinstance(normal, VariableIdentifier) and isinstance(normal.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(normal, self, dict())
            return self._refinement.visit(normal, evaluation, SignLattice().true(), self)
        elif isinstance(normal, UnaryBooleanOperation):
            if normal.operator == UnaryBooleanOperation.Operator.Neg:
                if isinstance(normal.expression, VariableIdentifier):
                    if isinstance(normal.expression.typ, BooleanLyraType):
                        evaluation = self._evaluation.visit(normal, self, dict())
                        false = SignLattice().false()
                        return self._refinement.visit(normal.expression, evaluation, false, self)
        elif isinstance(normal, BinaryBooleanOperation):
            return self._assume_binarybooleanoperation(normal)
        elif isinstance(normal, BinaryComparisonOperation):
            evaluation = self._evaluation.visit(normal.left, self, dict())
            non_positive = SignLattice(True, True, False)
            return self._refinement.visit(normal.left, evaluation, non_positive, self)
        error = f"Assumption of a {normal.__class__.__name__} expression is unsupported!"
        raise ValueError(error)

    # expression evaluation

    class ExpressionEvaluation(Basis.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the sign lattice."""

        @copy_docstring(Basis.ExpressionEvaluation.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = SignLattice.from_literal(expr)
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between instances
