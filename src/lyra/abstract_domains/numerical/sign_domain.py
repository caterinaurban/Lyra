"""
Sign Abstract Domain
====================

Non-relational abstract domain to be used for **numerical analysis**.
The set of possible numerical values of a program variable in a program state
is represented by their sign (negative, zero, positive, ...).

:Author: Jérôme Dohrau and Caterina Urban
"""
from collections import defaultdict

from lyra.abstract_domains.basis import BasisWithSummarization
from lyra.abstract_domains.lattice import ArithmeticMixin, BooleanMixin
from lyra.abstract_domains.state import State
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
                return cls(False, False, True)
            assert literal.val == "False"
            return cls(False, True, False)
        elif isinstance(literal.typ, IntegerLyraType):
            value = int(literal.val)
            return cls(value < 0, value == 0, value > 0)
        elif isinstance(literal.typ, FloatLyraType):
            value = float(literal.val)
            return cls(value < 0.0, value == 0.0, value > 0.0)
        return cls()

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
        return self._replace(type(self)(False, False, False))

    @copy_docstring(ArithmeticMixin.top)
    def top(self) -> 'SignLattice':
        return self._replace(type(self)(True, True, True))

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
        return self._replace(type(self)(negative, zero, positive))

    @copy_docstring(ArithmeticMixin._meet)
    def _meet(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative() and other.maybe_negative()
        zero = self.maybe_zero() and other.maybe_zero()
        positive = self.maybe_positive() and other.maybe_positive()
        return self._replace(type(self)(negative, zero, positive))

    @copy_docstring(ArithmeticMixin._widening)
    def _widening(self, other: 'SignLattice') -> 'SignLattice':
        return self._join(other)

    # arithmetic operations

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'SignLattice':
        negative = self.maybe_positive()
        zero = self.maybe_zero()
        positive = self.maybe_negative()
        return self._replace(type(self)(negative, zero, positive))

    def _add(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative() or other.maybe_negative()
        positive = self.maybe_positive() or other.maybe_positive()
        zero = (self.maybe_zero() and other.maybe_zero()) or \
               (self.maybe_negative() and other.maybe_positive()) or \
               (self.maybe_positive() and other.maybe_negative())
        return self._replace(type(self)(negative, zero, positive))

    def _sub(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative() or other.maybe_positive()
        positive = self.maybe_positive() or other.maybe_negative()
        zero = (self.maybe_zero() and other.maybe_zero()) or \
               (self.maybe_negative() and other.maybe_negative()) or \
               (self.maybe_positive() and other.maybe_positive())
        return self._replace(type(self)(negative, zero, positive))

    def _mult(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative() and other.maybe_positive()) or \
                   (self.maybe_positive() and other.maybe_negative())
        positive = (self.maybe_negative() and other.maybe_negative()) or \
                   (self.maybe_positive() and other.maybe_positive())
        zero = self.maybe_zero() or other.maybe_zero()
        return self._replace(type(self)(negative, zero, positive))

    def _div(self, other: 'SignLattice') -> 'SignLattice':
        return self._replace(type(self)())

    def _mod(self, other: 'SignLattice') -> 'SignLattice':
        return self._replace(type(self)())

    # boolean operations

    @copy_docstring(BooleanMixin.false)
    def false(self) -> 'SignLattice':
        """The false lattice element is ``=0``."""
        self._replace(type(self)(False, True, False))
        return self

    @copy_docstring(BooleanMixin.true)
    def true(self) -> 'SignLattice':
        """The true lattice element is ``>0``."""
        self._replace(type(self)(False, False, True))
        return self

    @copy_docstring(BooleanMixin.maybe)
    def maybe(self) -> 'SignLattice':
        """The maybe lattice element is ``≥0``."""
        self._replace(type(self)(False, True, True))
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


class SignState(BasisWithSummarization):
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

    @copy_docstring(BasisWithSummarization._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'SignState':
        if isinstance(condition.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(condition, self, dict())
            if neg:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).false()
            else:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).true()
            return self._refinement.visit(condition, evaluation, value, self)
        raise ValueError(f"Assumption of variable {condition} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_subscription)
    def _assume_subscription(self, condition: Subscription, neg: bool = False) -> 'SignState':
        if isinstance(condition.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(condition, self, dict())
            if neg:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).false()
            else:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).true()
            if not value.less_equal(evaluation[condition.target]):
                return self.bottom()
            return self
        raise ValueError(f"Assumption of variable {condition} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        # left == right -> left - right <= 0 && right - left <= 0
        zero = Literal(IntegerLyraType(), "0")
        minus = BinaryArithmeticOperation.Operator.Sub
        operator = BinaryComparisonOperation.Operator.LtE
        expr1 = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, condition.right)
        expr1 = BinaryComparisonOperation(condition.typ, expr1, operator, zero)
        expr2 = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, condition.left)
        expr2 = BinaryComparisonOperation(condition.typ, expr2, operator, zero)
        conj = BinaryBooleanOperation.Operator.And
        return self._assume_binary_boolean(BinaryBooleanOperation(condition.typ, expr1, conj, expr2), bwd=bwd)

    @copy_docstring(BasisWithSummarization._assume_noteq_comparison)
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        # left != right -> left - (right - 1) <= 0 || right - (left - 1) <= 0
        zero = Literal(IntegerLyraType(), "0")
        one = Literal(IntegerLyraType(), "1")
        minus = BinaryArithmeticOperation.Operator.Sub
        operator = BinaryComparisonOperation.Operator.LtE
        expr1 = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, one)
        expr1 = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, expr1)
        expr1 = BinaryComparisonOperation(condition.typ, expr1, operator, zero)
        expr2 = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, one)
        expr2 = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, expr2)
        expr2 = BinaryComparisonOperation(condition.typ, expr2, operator, zero)
        disj = BinaryBooleanOperation.Operator.Or
        return self._assume_binary_boolean(BinaryBooleanOperation(condition.typ, expr1, disj, expr2), bwd=bwd)

    @copy_docstring(BasisWithSummarization._assume_lt_comparison)
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        # left < right -> left - (right - 1) <= 0
        zero = Literal(IntegerLyraType(), "0")
        minus = BinaryArithmeticOperation.Operator.Sub
        one = Literal(IntegerLyraType(), "1")
        right = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, one)
        left = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, right)
        operator = BinaryComparisonOperation.Operator.LtE
        normal = BinaryComparisonOperation(condition.typ, left, operator, zero)
        evaluation = self._evaluation.visit(normal.left, self, dict())
        nonpositive = self.lattices[normal.typ](True, True, False)
        return self._refinement.visit(normal.left, evaluation, nonpositive, self)

    @copy_docstring(BasisWithSummarization._assume_lte_comparison)
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        # left <= right -> left - right <= 0
        zero = Literal(IntegerLyraType(), "0")
        if isinstance(condition.right, Literal) and condition.right == zero:
            normal = condition
        else:
            minus = BinaryArithmeticOperation.Operator.Sub
            left = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, condition.right)
            normal = BinaryComparisonOperation(condition.typ, left, condition.operator, zero)
        evaluation = self._evaluation.visit(normal.left, self, dict())
        nonpositive = self.lattices[normal.typ](True, True, False)
        return self._refinement.visit(normal.left, evaluation, nonpositive, self)

    @copy_docstring(BasisWithSummarization._assume_gt_comparison)
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        # left > right -> right - (left - 1) <= 0
        zero = Literal(IntegerLyraType(), "0")
        one = Literal(IntegerLyraType(), "1")
        minus = BinaryArithmeticOperation.Operator.Sub
        left = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, one)
        right = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, left)
        operator = BinaryComparisonOperation.Operator.LtE
        normal = BinaryComparisonOperation(condition.typ, right, operator, zero)
        evaluation = self._evaluation.visit(normal.left, self, dict())
        nonpositive = self.lattices[normal.typ](True, True, False)
        return self._refinement.visit(normal.left, evaluation, nonpositive, self)

    @copy_docstring(BasisWithSummarization._assume_gte_comparison)
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        # left >= right -> right - left <= 0
        zero = Literal(IntegerLyraType(), "0")
        minus = BinaryArithmeticOperation.Operator.Sub
        right = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, condition.left)
        operator = BinaryComparisonOperation.Operator.LtE
        normal = BinaryComparisonOperation(condition.typ, right, operator, zero)
        evaluation = self._evaluation.visit(normal.left, self, dict())
        nonpositive = self.lattices[normal.typ](True, True, False)
        return self._refinement.visit(normal.left, evaluation, nonpositive, self)

    @copy_docstring(BasisWithSummarization._assume_is_comparison)
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        raise ValueError(f"Assumption of a binary comparison with {condition.operator} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        raise ValueError(f"Assumption of a binary comparison with {condition.operator} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        if condition.forloop and not bwd:  # assumption in a for loop during forward analysis
            top = self.lattices[condition.left.typ](**self.arguments[condition.left.typ]).top()
            left = defaultdict(lambda: top)
        else:  # condition assumption
            left = self._evaluation.visit(condition.left, self, dict())
        right = self._evaluation.visit(condition.right, self, dict())
        return self._refinement.visit(condition.left, left, right[condition.right], self)

    @copy_docstring(BasisWithSummarization._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SignState':
        return self

    # expression evaluation

    class ExpressionEvaluation(BasisWithSummarization.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the sign lattice."""

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = state.lattices[expr.typ].from_literal(expr)
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between instances
