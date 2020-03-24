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

from apronpy.box import PyBox
from apronpy.manager import PyManager, PyBoxMPQManager

from lyra.abstract_domains.basis import BasisWithSummarization
from lyra.abstract_domains.lattice import BottomMixin, ArithmeticMixin, BooleanMixin, SequenceMixin
from lyra.abstract_domains.numerical.apron_domain import APRONStateWithSummarization
from lyra.abstract_domains.state import State
from lyra.core.expressions import *

from lyra.core.utils import copy_docstring
from lyra.core.types import BooleanLyraType, IntegerLyraType, FloatLyraType, SequenceLyraType, ContainerLyraType


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


class IntervalState(BasisWithSummarization):
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
        for v in self.variables:
            if isinstance(v.typ, (SequenceLyraType, ContainerLyraType)) and not v.special:
                self.store[LengthIdentifier(v)] = lattices[IntegerLyraType()](lower=0)

    @copy_docstring(BasisWithSummarization.is_bottom)
    def is_bottom(self) -> bool:
        """The current state is bottom if `any` non-summary variable maps to a bottom element,
        or if the length identifier of `any` summary variable maps to a bottom element."""
        for var, element in self.store.items():
            if not var.special:
                if isinstance(var.typ, (SequenceLyraType, ContainerLyraType)):
                    if element.is_bottom() and self.store[LengthIdentifier(var)].is_bottom():
                        return True
                elif element.is_bottom():
                    return True
        return False

    @copy_docstring(BasisWithSummarization._assign_dictionary_subscription)
    def _assign_dictionary_subscription(self, left: Subscription, right: Expression):
        # update length identifier
        target = left
        key = None
        while isinstance(target, Subscription):  # recurse to VariableIdentifier target
            key = target.key
            target = target.target
        _evaluation = self._evaluation.visit(key, self, dict())
        current = self.store[LengthIdentifier(target)]      # current length
        one = self.lattices[IntegerLyraType()](lower=1, upper=1)
        if _evaluation[key].less_equal(self.store[KeysIdentifier(target)]):
            self.store[LengthIdentifier(target)] = deepcopy(current).join(current.add(one))
        else:
            self.store[LengthIdentifier(target)] = current.add(one)
        # perform the assignment
        super()._assign_dictionary_subscription(left, right)
        return self

    @copy_docstring(BasisWithSummarization._assign)
    def _assign(self, left: Expression, right: Expression) -> 'IntervalState':
        # update length identifiers, if appropriate
        if isinstance(left, VariableIdentifier):
            if isinstance(left.typ, (SequenceLyraType, ContainerLyraType)) and not left.special:
                self.store[LengthIdentifier(left)] = self._length.visit(right, self)
        elif isinstance(left, Subscription) and isinstance(left.target, VariableIdentifier):
            if isinstance(left.target.typ, SequenceLyraType):
                length = self.store[LengthIdentifier(left.target)]
                key = deepcopy(self._evaluation.visit(left.key, self, dict())[left.key])
                if key.less_equal(self.lattices[left.key.typ](lower=0)):    # key is positive
                    if length.upper < key.lower:    # key is definitely larger than length
                        return self.bottom()
                    lower = self.lattices[left.key.typ](lower=key.lower)
                    self.store[LengthIdentifier(left.target)] = length.meet(lower)
                elif key.less_equal(self.lattices[left.key.typ](upper=-1)):     # key is negative
                    if length.upper + key.upper < 0:    # key is definitely smaller than length
                        return self.bottom()
                    upper = self.lattices[left.key.typ](lower=-key.upper)
                    self.store[LengthIdentifier(left.target)] = length.meet(upper)
        elif isinstance(left, Slicing) and isinstance(left.target, VariableIdentifier): #x[i:j] = e
            if isinstance(left.target.typ, SequenceLyraType):   # x[i:j] = e
                current = self.store[LengthIdentifier(left.target)]      # current length
                # under-approximate length of left
                lattice = self.lattices[IntegerLyraType()]
                slicing = lattice(lower=1, upper=1)     # default under-approximation
                # over-approximate length of right
                extra = self._length.visit(right, self)
                # len(x) = len(x) - len(x[j:i]) + len(e)
                self.store[LengthIdentifier(left.target)] = current.sub(slicing).add(extra)
        # perform the assignment
        super()._assign(left, right)
        return self

    @copy_docstring(BasisWithSummarization._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'IntervalState':
        if isinstance(condition.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(condition, self, dict())
            if neg:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).false()
            else:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).true()
            return self._refinement.visit(condition, evaluation, value, self)
        raise ValueError(f"Assumption of variable {condition} is unsupported!")

    @copy_docstring(BasisWithSummarization._weak_update)
    def _weak_update(self, variables: Set[VariableIdentifier], previous: 'BasisWithSummarization'):
        for var in variables:
            self.store[var].join(previous.store[var])
            if isinstance(var.typ, (SequenceLyraType, ContainerLyraType)) and not var.special:
                self.store[LengthIdentifier(var)].join(previous.store[LengthIdentifier(var)])
        return self

    @copy_docstring(BasisWithSummarization._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
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
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
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
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
        # left < right -> left - (right - 1) <= 0
        zero = Literal(IntegerLyraType(), "0")
        minus = BinaryArithmeticOperation.Operator.Sub
        one = Literal(IntegerLyraType(), "1")
        right = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, one)
        left = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, right)
        operator = BinaryComparisonOperation.Operator.LtE
        normal = BinaryComparisonOperation(condition.typ, left, operator, zero)
        evaluation = self._evaluation.visit(normal.left, self, dict())
        nonpositive = self.lattices[normal.typ](upper=0)
        return self._refinement.visit(normal.left, evaluation, nonpositive, self)

    @copy_docstring(BasisWithSummarization._assume_lte_comparison)
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
        # left <= right -> left - right <= 0
        zero = Literal(IntegerLyraType(), "0")
        if isinstance(condition.right, Literal) and condition.right == zero:
            normal = condition
        else:
            minus = BinaryArithmeticOperation.Operator.Sub
            left = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, condition.right)
            normal = BinaryComparisonOperation(condition.typ, left, condition.operator, zero)
        evaluation = self._evaluation.visit(normal.left, self, dict())
        nonpositive = self.lattices[normal.typ](upper=0)
        return self._refinement.visit(normal.left, evaluation, nonpositive, self)

    @copy_docstring(BasisWithSummarization._assume_gt_comparison)
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
        # left > right -> right - (left - 1) <= 0
        zero = Literal(IntegerLyraType(), "0")
        one = Literal(IntegerLyraType(), "1")
        minus = BinaryArithmeticOperation.Operator.Sub
        left = BinaryArithmeticOperation(condition.left.typ, condition.left, minus, one)
        right = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, left)
        operator = BinaryComparisonOperation.Operator.LtE
        normal = BinaryComparisonOperation(condition.typ, right, operator, zero)
        evaluation = self._evaluation.visit(normal.left, self, dict())
        nonpositive = self.lattices[normal.typ](upper=0)
        return self._refinement.visit(normal.left, evaluation, nonpositive, self)

    @copy_docstring(BasisWithSummarization._assume_gte_comparison)
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
        # left >= right -> right - left <= 0
        zero = Literal(IntegerLyraType(), "0")
        minus = BinaryArithmeticOperation.Operator.Sub
        right = BinaryArithmeticOperation(condition.right.typ, condition.right, minus, condition.left)
        operator = BinaryComparisonOperation.Operator.LtE
        normal = BinaryComparisonOperation(condition.typ, right, operator, zero)
        evaluation = self._evaluation.visit(normal.left, self, dict())
        nonpositive = self.lattices[normal.typ](upper=0)
        return self._refinement.visit(normal.left, evaluation, nonpositive, self)

    @copy_docstring(BasisWithSummarization._assume_is_comparison)
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
        raise ValueError(f"Assumption of a binary comparison with {condition.operator} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
        raise ValueError(f"Assumption of a binary comparison with {condition.operator} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
        if condition.forloop and not bwd:  # assumption in a for loop during forward analysis
            top = self.lattices[condition.left.typ](**self.arguments[condition.left.typ]).top()
            left = defaultdict(lambda: top)
        else:  # condition assumption
            left = self._evaluation.visit(condition.left, self, dict())
        right = self._evaluation.visit(condition.right, self, dict())
        return self._refinement.visit(condition.left, left, right[condition.right], self)

    @copy_docstring(BasisWithSummarization._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'IntervalState':
        return self

    # expression evaluation

    class ExpressionEvaluation(BasisWithSummarization.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the interval lattice."""

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation    # nothing to be done
            evaluation[expr] = state.lattices[expr.typ].from_literal(expr)
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done

            evaluated = evaluation
            evaluated = self.visit(expr.start, state, evaluated)
            sub = BinaryArithmeticOperation.Operator.Sub
            one = Literal(expr.stop.typ, '1')
            stop = BinaryArithmeticOperation(expr.stop.typ, expr.stop, sub, one)
            evaluated = self.visit(stop, state, evaluated)

            if not evaluated[expr.start].is_bottom() and not evaluated[stop].is_bottom():
                lower = evaluated[expr.start].lower
                upper = evaluated[stop].upper
                value = state.lattices[expr.typ](lower=lower, upper=upper)
                evaluation[expr] = value
            else:
                evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances

    class LengthEvaluation(ExpressionVisitor):
        """Visitor that computes the length of a sequence type expression."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None):
            if isinstance(expr.typ, StringLyraType):
                return state.lattices[IntegerLyraType()](len(expr.val), len(expr.val))
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None):
            if isinstance(expr.typ, SequenceLyraType) and not expr.special:
                length = LengthIdentifier(expr)
                return state.store.get(length, state.lattices[IntegerLyraType()](lower=0))
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr: LengthIdentifier, state=None):
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None):
            return state.lattices[IntegerLyraType()](len(expr.items), len(expr.items))

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, state=None):
            return state.lattices[IntegerLyraType()](len(expr.items), len(expr.items))

        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, state=None):
            return state.lattices[IntegerLyraType()](len(expr.items), len(expr.items))

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, state=None):
            return state.lattices[IntegerLyraType()](len(expr.keys), len(expr.keys))

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None):
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None):
            return state.lattices[IntegerLyraType()](lower=1, upper=1)

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None):
            lattice = state.lattices[IntegerLyraType()]

            def is_one(stride):
                literal = isinstance(stride, Literal)
                return literal and lattice(stride).less_equal(lattice(lower=1, upper=1))

            if isinstance(expr.lower, Literal):
                lower = IntervalLattice.from_literal(expr.lower)
                if not lower.less_equal(lattice(lower=0)):
                    lower = lower.add(state.store[LengthIdentifier(expr.target)])
                if not expr.upper:
                    upper = deepcopy(state.store[LengthIdentifier(expr.target)])
                    if not expr.stride or is_one(expr.stride):  # [l:_:(1)]
                        length = lattice(lower=0).meet(upper.sub(lower))
                        if length.is_bottom():
                            return lattice(lower=0, upper=0)
                        return length
                elif isinstance(expr.upper, Literal):
                    upper = IntervalLattice.from_literal(expr.upper)
                    if not upper.less_equal(lattice(lower=0)):
                        upper = upper.add(state.store[LengthIdentifier(expr.target)])
                    if not expr.stride or is_one(expr.stride):  # [l:u:(1)]
                        length = lattice(lower=0).meet(upper.sub(lower))
                        if length.is_bottom():
                            return lattice(lower=0, upper=0)
                        return length
            return deepcopy(state.store[LengthIdentifier(expr.target)])   # over-approximation

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None):
            return state.lattices[IntegerLyraType()](lower=0)

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None):
            literal1 = isinstance(expr.start, Literal)
            literal2 = isinstance(expr.stop, Literal)
            variable2 = isinstance(expr.stop, VariableIdentifier)
            literal3 = isinstance(expr.step, Literal)
            if literal1 and literal2 and literal3:
                start = int(expr.start.val)
                stop = int(expr.stop.val)
                step = int(expr.step.val)
                length = len(range(start, stop, step))
                return state.lattices[IntegerLyraType()](lower=length, upper=length)
            elif literal1 and variable2 and literal3:
                start = int(expr.start.val)
                stop = state.store[expr.stop]
                return state.lattices[IntegerLyraType()](lower=start).meet(stop)
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_Keys)
        def visit_Keys(self, expr: Keys, state=None):
            return state.lattices[IntegerLyraType()](lower=0)

        @copy_docstring(ExpressionVisitor.visit_Values)
        def visit_Values(self, expr: Values, state=None):
            return state.lattices[IntegerLyraType()](lower=0)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, state=None):
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, state=None):
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, state=None):
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
        def visit_BinarySequenceOperation(self, expr, state=None):
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                left = self.visit(expr.left, state)
                right = self.visit(expr.right, state)
                return left.add(right)
            raise ValueError(f"Binary sequence operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            raise ValueError(f"Unexpected expression during sequence length computation.")

    _length = LengthEvaluation()  # static class member shared between all instances


class BoxStateWithSummarization(APRONStateWithSummarization):
    """Interval analysis state based on APRON. An element of the interval abstract domain.

    .. document private methods
    .. automethod:: BoxState._assign
    .. automethod:: BoxState._assume
    .. automethod:: BoxState._output
    .. automethod:: BoxState._substitute

    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        super().__init__(PyBox, variables, precursory=precursory)

    def __repr__(self):
        def var(dim):
            return self.environment.environment.contents.var_of_dim[dim].decode('utf-8')
        def itv(dim):
            bound = self.bound_variable(PyVar(var(dim)))
            interval = bound.interval.contents
            inf = '{}'.format(interval.inf.contents)
            lower = inf if inf != '-1/0' else '-inf'
            sup = '{}'.format(interval.sup.contents)
            upper = sup if sup != '1/0' else 'inf'
            return '[{}, {}]'.format(lower, upper)
        if self.is_bottom():
            return "⊥"
        env = self.environment.environment.contents
        result = ', '.join('{}: {}'.format(var(i), itv(i)) for i in range(env.intdim))
        result += ', '.join(
            '{} -> {}'.format(var(env.intdim + i), itv(env.intdim + i)) for i in range(env.realdim)
        )
        return result.replace('.0', '')

    manager: PyManager = PyBoxMPQManager()
