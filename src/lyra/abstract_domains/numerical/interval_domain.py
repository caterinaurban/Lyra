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
from typing import Union

from apronpy.box import PyBox
from apronpy.manager import PyManager, PyBoxMPQManager

from lyra.abstract_domains.basis import BasisWithSummarization, Basis
from lyra.abstract_domains.container.indexed_lattice import IndexedLattice
from lyra.abstract_domains.numerical.apron_domain import APRONStateWithSummarization
from lyra.abstract_domains.numerical.interval_lattice import IntervalLattice
from lyra.abstract_domains.state import State
from lyra.core.expressions import *

from lyra.core.utils import copy_docstring
from lyra.core.types import BooleanLyraType, IntegerLyraType, SequenceLyraType, FloatLyraType


class IntervalStateMixin(BasisWithSummarization):

    @copy_docstring(BasisWithSummarization.is_top)
    def is_top(self) -> bool:
        """The current store is top if `all` of its variables map to a top element."""
        _store = all(element.is_top() for element in self.store.values())
        _top = self.lattices[IntegerLyraType()](lower=0)
        _lengths = all(_top.less_equal(element) for element in self.lengths.values())
        return _store and _lengths

    @copy_docstring(BasisWithSummarization._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression):
        if left.has_length:  # update corresponding length identifier, if any
            self.lengths[left.length] = self._length.visit(right, self)
        # perform the assignment
        super()._assign_variable(left, right)
        return self

    @copy_docstring(BasisWithSummarization._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False):
        if isinstance(condition.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(condition, self, dict())
            if neg:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).false()
            else:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).true()
            return self._refinement.visit(condition, evaluation, value, self)
        raise ValueError(f"Assumption of variable {condition} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
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
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
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
        return self._assume_binary_boolean(
            BinaryBooleanOperation(condition.typ, expr1, disj, expr2), bwd=bwd)

    @copy_docstring(BasisWithSummarization._assume_lt_comparison)
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
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
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
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
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
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
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
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
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        error = f"Assumption of a binary comparison with {condition.operator} is unsupported!"
        raise ValueError(error)

    @copy_docstring(BasisWithSummarization._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        error = f"Assumption of a binary comparison with {condition.operator} is unsupported!"
        raise ValueError(error)

    @copy_docstring(BasisWithSummarization._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        if condition.forloop and not bwd:  # assumption in a for loop during forward analysis
            top = self.lattices[condition.left.typ](**self.arguments[condition.left.typ]).top()
            left = defaultdict(lambda: top)
        else:  # condition assumption
            left = self._evaluation.visit(condition.left, self, dict())
        right = self._evaluation.visit(condition.right, self, dict())
        return self._refinement.visit(condition.left, left, right[condition.right], self)

    @copy_docstring(BasisWithSummarization._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    @copy_docstring(State.forget_variable)
    def forget_variable(self, variable: VariableIdentifier):
        super().forget_variable(variable)
        if variable.has_length:
            self.lengths[variable.length] = self.lattices[IntegerLyraType()](lower=0)
        return self

    # length evaluation

    class LengthEvaluation(ExpressionVisitor):
        """Visitor that computes the length of a sequence type expression."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None):
            if isinstance(expr.typ, StringLyraType):
                return state.lattices[IntegerLyraType()](len(expr.val), len(expr.val))
            raise ValueError(f"Unexpected expression during sequence length computation.")

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None):
            if expr.has_length:
                return state.lengths.get(expr.length, state.lattices[IntegerLyraType()](lower=0))
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
            case0 = isinstance(expr.target.typ, StringLyraType)
            sequence = isinstance(expr.target.typ, (ListLyraType, TupleLyraType))
            complex = (SequenceLyraType, DictLyraType)
            case1 = sequence and not isinstance(expr.target.typ.typ, complex)
            dictionary = isinstance(expr.target.typ, DictLyraType)
            case2 = dictionary and not isinstance(expr.target.typ.val_typ, complex)
            if case0 or case1 or case2:
                return state.lattices[IntegerLyraType()](lower=1, upper=1)
            return state.lattices[IntegerLyraType()](lower=0)

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None):
            lattice = state.lattices[IntegerLyraType()]

            def is_one(stride):
                literal = isinstance(stride, Literal)
                return literal and lattice(stride).less_equal(lattice(lower=1, upper=1))

            if isinstance(expr.target, VariableIdentifier):
                if isinstance(expr.lower, Literal):
                    lower = IntervalLattice.from_literal(expr.lower)
                    if not lower.less_equal(lattice(lower=0)):
                        lower = lower.add(state.lengths[LengthIdentifier(expr.target)])
                    if not expr.upper:
                        upper = deepcopy(state.lengths[LengthIdentifier(expr.target)])
                        if not expr.stride or is_one(expr.stride):  # [l:_:(1)]
                            length = lattice(lower=0).meet(upper.sub(lower))
                            if length.is_bottom():
                                return lattice(lower=0, upper=0)
                            return length
                    elif isinstance(expr.upper, Literal):
                        upper = IntervalLattice.from_literal(expr.upper)
                        if not upper.less_equal(lattice(lower=0)):
                            upper = upper.add(state.lengths[LengthIdentifier(expr.target)])
                        if not expr.stride or is_one(expr.stride):  # [l:u:(1)]
                            length = lattice(lower=0).meet(upper.sub(lower))
                            if length.is_bottom():
                                return lattice(lower=0, upper=0)
                            return length
                return deepcopy(state.lengths[LengthIdentifier(expr.target)])   # over-approximation
            return lattice(lower=0)     # default

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

        @copy_docstring(ExpressionVisitor.visit_CastOperation)
        def visit_CastOperation(self, expr: CastOperation, state=None):
            if isinstance(expr.typ, (SequenceLyraType, ContainerLyraType)):
                return self.visit(expr.expression, state)
            raise ValueError(f"Unexpected expression during sequence length computation.")

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


class IntervalStateWithSummarization(IntervalStateMixin, BasisWithSummarization):
    """Interval analysis state. An element of the interval abstract domain.

    Map from each program variable to the interval representing its value.
    The value of all program variables is represented by the unbounded interval by default.

    .. note:: Program variables storing sequences and containers are abstracted via summarization.

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
            if v.has_length:
                self.lengths[v.length] = lattices[IntegerLyraType()](lower=0)

    @copy_docstring(BasisWithSummarization._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'IntervalStateWithSummarization':
        # update length identifiers, if appropriate
        target = left.target
        if isinstance(target, VariableIdentifier) and isinstance(target.typ, SequenceLyraType):
            current: IntervalLattice = self.lengths[target.length]   # current length
            key = deepcopy(self._evaluation.visit(left.key, self, dict())[left.key])
            if key.less_equal(self.lattices[left.key.typ](lower=0)):  # key is positive
                if current.upper < key.lower:  # key is definitely larger than length
                    return self.bottom()
                lower = self.lattices[left.key.typ](lower=key.lower + 1)
                self.lengths[target.length] = current.meet(lower)
            elif key.less_equal(self.lattices[left.key.typ](upper=-1)):  # key is negative
                if current.upper + key.upper < 0:  # key is definitely smaller than length
                    return self.bottom()
                upper = self.lattices[left.key.typ](lower=-key.upper)
                self.lengths[target.length] = current.meet(upper)
        elif isinstance(target, VariableIdentifier) and target.is_dictionary:  # D[key] = value
            current: IntervalLattice = self.lengths[target.length]   # current length
            key = self._evaluation.visit(left.key, self, dict())[left.key]      # evaluate key
            one = self.lattices[IntegerLyraType()](lower=1, upper=1)
            if key.upper == key.lower and not key.less_equal(self.keys[left.target.keys]):
                self.lengths[target.length] = current.add(one)
            else:
                self.lengths[target.length] = deepcopy(current).join(current.add(one))
        # perform the assignment
        super()._assign_subscription(left, right)
        return self

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'IntervalStateWithSummarization':
        # update length identifiers, if appropriate
        target = left.target
        if isinstance(target, VariableIdentifier) and isinstance(target.typ, SequenceLyraType):
            current: IntervalLattice = self.lengths[target.length]   # current length
            # under-approximate length of left
            lattice = self.lattices[IntegerLyraType()]
            slicing = lattice(lower=1, upper=1)  # default under-approximation
            # over-approximate length of right
            extra = self._length.visit(right, self)
            # len(x) = len(x) - len(x[j:i]) + len(e)
            self.lengths[target.length] = current.sub(slicing).add(extra)
        # perform the assignment
        super()._assign_slicing(left, right)
        return self

    @copy_docstring(BasisWithSummarization._assume_subscription)
    def _assume_subscription(self, condition: Subscription, neg: bool = False):
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


class IntervalStateWithIndexing(IntervalStateMixin, BasisWithSummarization):
    """Interval analysis state with indexing.

    .. note:: Program variables storing sequences and dictionaries are abstracted via indexing,
    other containers, i.e., sets are abstracted via summarization.

    .. document private methods
    .. automethod:: IntervalStateWithIndexing._assign
    .. automethod:: IntervalStateWithIndexing._assume
    .. automethod:: IntervalStateWithIndexing._output
    .. automethod:: IntervalStateWithIndexing._substitute

    """
    bound: int

    class Lattices(defaultdict):

        def __missing__(self, key):
            if isinstance(key, (SequenceLyraType, DictLyraType)):
                return IndexedLattice
            return IntervalLattice

    class Arguments(defaultdict):

        def __missing__(self, key):
            if isinstance(key, (SequenceLyraType, DictLyraType)):
                return {'lattice': IntervalLattice, 'bound': IntervalStateWithIndexing.bound}
            return {}

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        """Map each program variable to the interval representing its value.

        :param variables: set of program variables
        """
        lattices = IntervalStateWithIndexing.Lattices()
        arguments = IntervalStateWithIndexing.Arguments()
        super().__init__(variables, lattices, arguments, precursory=precursory)
        for v in self.variables:
            if v.has_length:
                self.lengths[v.length] = lattices[IntegerLyraType()](lower=0)

    def _assign_subscription(self, left: Subscription, right: Expression):
        value = self._evaluation.visit(right, self, dict())[right]          # evaluate value
        if isinstance(value, IntervalLattice):
            itv: IntervalLattice = deepcopy(value)
        elif isinstance(left.target.typ.val_typ, DictLyraType):
            itv: IntervalLattice = value.summarize(keys=left.target.typ.val_typ.key_typ)
        else:
            itv: IntervalLattice = value.summarize()
        if isinstance(left.target, VariableIdentifier):
            target: IndexedLattice = self._evaluation.visit(left.target, self, dict())[left.target]
            key = self._evaluation.visit(left.key, self, dict())[left.key]
            _key: List[str] = self._key.visit(left.key, target.bound, self)
            precise = len(_key) == 1 and _key[0] != target.default
            added = False
            replaced = False
            if precise:
                added = _key[0] not in target.used and target.default not in target.used
                replaced = _key[0] in target.used
                self.store[left.target][_key[0]] = itv
            else:
                self.store[left.target].weak_set(_key, itv)
            if left.target.is_dictionary:
                # update length
                current: IntervalLattice = self.lengths[left.target.length]  # current length
                one = self.lattices[IntegerLyraType()](lower=1, upper=1)
                if precise:
                    if added:
                        self.lengths[left.target.length] = current.add(one)
                    elif not replaced:
                        self.lengths[left.target.length] = deepcopy(current).join(current.add(one))
                else:
                    self.lengths[left.target.length] = deepcopy(current).join(current.add(one))
                # update keys
                self.keys[left.target.keys] = self.keys[left.target.keys].join(deepcopy(key))
                # update values
                summary = self.store[left.target].summarize()
                values = left.target.values
                if isinstance(self.values[values], IntervalLattice):
                    self.values[values] = self.values[values].join(deepcopy(itv)).meet(summary)
                else:
                    assert isinstance(self.values[values], IndexedLattice)
                    assert isinstance(value, IndexedLattice)
                    updated = self.values[values].join(deepcopy(value)).refine(summary)
                    self.values[values] = updated
            else:
                current: IntervalLattice = self.lengths[left.target.length]  # current length
                if key.less_equal(self.lattices[left.key.typ](lower=0)):  # key is positive
                    if current.upper < key.lower:  # key is definitely larger than length
                        return self.bottom()
                    lower = self.lattices[left.key.typ](lower=key.lower + 1)
                    self.lengths[left.target.length] = current.meet(lower)
                elif key.less_equal(self.lattices[left.key.typ](upper=-1)):  # key is negative
                    if current.upper + key.upper < 0:  # key is definitely smaller than length
                        return self.bottom()
                    upper = self.lattices[left.key.typ](lower=-key.upper)
                    self.lengths[left.target.length] = current.meet(upper)
        elif isinstance(left.target.typ, DictLyraType):
            key = self._evaluation.visit(left.key, self, dict())[left.key]
            _itv = deepcopy(key) if isinstance(key, IntervalLattice) else key.summarize()
            _target = left.target.target
            _key = left.target.key
            __key = left.key
            while isinstance(_target, Subscription):
                __key = _key
                _key = _target.key
                _target = _target.target
            assert isinstance(_target, VariableIdentifier)
            target = self._evaluation.visit(_target, self, dict())[_target]
            _key: List[str] = self._key.visit(_key, target.bound, self)
            self.store[_target].weak_set(_key, deepcopy(itv).join(deepcopy(_itv)))
            if _target.is_dictionary:
                # update values
                summary = self.store[_target].summarize()
                values = _target.values
                if isinstance(self.values[values], IntervalLattice):
                    self.values[values] = self.values[values].join(deepcopy(itv)).meet(summary)
                else:
                    assert isinstance(self.values[values], IndexedLattice)
                    __key: List[str] = self._key.visit(__key, target.bound, self)
                    self.values[values].weak_set(__key, itv)
                    self.values[values] = self.values[values].refine(summary)
        else:
            _target = left.target.target
            _key = left.target.key
            __key = left.key
            while isinstance(_target, Subscription):
                __key = _key
                _key = _target.key
                _target = _target.target
            if isinstance(_target, Slicing):
                return self
            assert isinstance(_target, VariableIdentifier)
            target = self._evaluation.visit(_target, self, dict())[_target]
            _key: List[str] = self._key.visit(_key, target.bound, self)
            self.store[_target].weak_set(_key, itv)
            if _target.is_dictionary:
                # update values
                summary = self.store[_target].summarize()
                values = _target.values
                if isinstance(self.values[values], IntervalLattice):
                    self.values[values] = self.values[values].join(deepcopy(itv)).meet(summary)
                else:
                    assert isinstance(self.values[values], IndexedLattice)
                    __key: List[str] = self._key.visit(__key, target.bound, self)
                    self.values[values].weak_set(__key, itv)
                    self.values[values] = self.values[values].refine(summary)
        return self

    def _assign_slicing(self, left: Slicing, right: Expression) -> 'State':
        pass

    @copy_docstring(BasisWithSummarization._assume_subscription)
    def _assume_subscription(self, condition: Subscription, neg: bool = False):
        if isinstance(condition.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(condition, self, dict())
            if neg:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).false()
            else:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).true()
            if not value.less_equal(evaluation[condition]):
                return self.bottom()
            return self
        raise ValueError(f"Assumption of variable {condition} is unsupported!")

    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'State':
        pass

    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'State':
        pass

    # key evaluation

    class KeyEvaluation(ExpressionVisitor):

        def visit_Literal(self, expr: 'Literal', bound=None, state=None) -> List[str]:
            return [str(expr)]

        def default(self, expr, bound=None, state=None) -> List[str]:
            current = state._evaluation.visit(expr, state, dict())[expr]
            itv = current if isinstance(current, IntervalLattice) else current.summarize()
            return itv.gamma(bound)

        def visit_VariableIdentifier(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_LengthIdentifier(self, expr: 'LengthIdentifier', bound=None, state=None):
            return self.default(expr, bound, state)

        def visit_ListDisplay(self, expr: 'ListDisplay', bound=None, state=None):
            raise ValueError(f"Unexpected expression during key evaluation.")

        def visit_TupleDisplay(self, expr: 'TupleDisplay', bound=None, state=None) -> List[str]:
            items = list()
            for item in expr.items:
                value: List[str] = self.visit(item, bound, state)
                if len(value) == 1:
                    items.append(value[0])
                else:
                    return ['_']
            return ['({})'.format(', '.join(items))]

        def visit_SetDisplay(self, expr: 'SetDisplay', bound=None, state=None):
            raise ValueError(f"Unexpected expression during key evaluation.")

        def visit_DictDisplay(self, expr: 'DictDisplay', bound=None, state=None):
            raise ValueError(f"Unexpected expression during key evaluation.")

        def visit_AttributeReference(self, expr: 'AttributeReference', bound=None, state=None):
            raise NotImplementedError(f"Unsupported expression during key evaluation.")

        def visit_Subscription(self, expr: 'Subscription', bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_Slicing(self, expr: 'Slicing', bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_Input(self, expr: 'Input', bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_Range(self, expr: 'Range', bound=None, state=None):
            raise NotImplementedError(f"Unsupported expression during key evaluation.")

        def visit_Keys(self, expr: 'Keys', bound=None, state=None):
            raise NotImplementedError(f"Unsupported expression during key evaluation.")

        def visit_Values(self, expr: 'Values', bound=None, state=None):
            raise NotImplementedError(f"Unsupported expression during key evaluation.")

        def visit_CastOperation(self, expr: 'CastOperation', bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_UnaryArithmeticOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_UnaryBooleanOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_BinaryArithmeticOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_BinarySequenceOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_BinaryBooleanOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_BinaryComparisonOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

    _key = KeyEvaluation()

    # expression evaluation

    class ExpressionEvaluation(BasisWithSummarization.ExpressionEvaluation):

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, StringLyraType):
                value = state.lattices[expr.typ](**state.arguments[expr.typ], index=dict())
                for idx, item in enumerate(expr.val):
                    value[str(idx)] = IntervalLattice()
                evaluation[expr] = value
            else:
                evaluation[expr] = state.lattices[expr.typ].from_literal(expr)
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_ListDisplay)
        def visit_ListDisplay(self, expr: 'ListDisplay', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ], index=dict())
            for idx, item in enumerate(expr.items):
                evaluated = self.visit(item, state, evaluated)
                current = evaluated[item]
                if isinstance(current, IntervalLattice):
                    itv = deepcopy(current)
                else:
                    itv = current.summarize()
                value[str(idx)] = itv
            evaluation[expr] = value
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: 'TupleDisplay', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ], index=dict())
            for idx, item in enumerate(expr.items):
                evaluated = self.visit(item, state, evaluated)
                current = evaluated[item]
                if isinstance(current, IntervalLattice):
                    itv = deepcopy(current)
                else:
                    itv = current.summarize()
                value[str(idx)] = itv
            evaluation[expr] = value
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_SetDisplay)
        def visit_SetDisplay(self, expr: 'SetDisplay', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                current = evaluated[item]
                if isinstance(current, IntervalLattice):
                    itv = deepcopy(current)
                else:
                    itv = current.summarize()
                value = value.join(itv)
            evaluation[expr] = value
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_DictDisplay)
        def visit_DictDisplay(self, expr: 'DictDisplay', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation   # nothing to be done
            evaluated = evaluation
            _value = state.lattices[expr.typ.key_typ](**state.arguments[expr.typ.key_typ]).bottom()
            value = state.lattices[expr.typ](**state.arguments[expr.typ], index=dict())
            value_ = state.lattices[expr.typ.val_typ](**state.arguments[expr.typ.val_typ]).bottom()
            for idx, (key, val) in enumerate(zip(expr.keys, expr.values)):
                evaluated = self.visit(key, state, evaluated)   # recurse on key
                _current: Union[IntervalLattice, IndexedLattice] = evaluated[key]
                _value = _value.join(deepcopy(_current))
                evaluated = self.visit(val, state, evaluated)   # recurse on val
                current_: Union[IntervalLattice, IndexedLattice] = evaluated[val]
                value_ = value_.join(deepcopy(current_))
                #
                if isinstance(current_, IntervalLattice):
                    itv_ = deepcopy(current_)
                elif isinstance(expr.typ.val_typ, DictLyraType):
                    itv_ = current_.summarize(keys=expr.typ.val_typ.key_typ)
                else:
                    itv_ = current_.summarize()
                _key: List[str] = state._key.visit(key, value.bound, state)
                if len(_key) == 1 and _key[0] != value.default:
                    value[_key[0]] = itv_
                else:
                    value[value.default] = itv_
            evaluation[KeysIdentifier(expr)] = _value
            evaluation[expr] = value
            evaluation[ValuesIdentifier(expr)] = value_
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Subscription)
        def visit_Subscription(self, expr: 'Subscription', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluated = self.visit(expr.target, state, evaluation)
            target = deepcopy(evaluated[expr.target])
            if isinstance(target, IntervalLattice):
                evaluation[expr] = target
            else:
                assert isinstance(target, IndexedLattice)
                _key: List[str] = state._key.visit(expr.key, target.bound, state)
                fetched: IntervalLattice = target.weak_get(_key)
                if isinstance(expr.target, VariableIdentifier) and expr.target.is_dictionary:
                    values = deepcopy(evaluated[expr.target.values])
                    if isinstance(values, IntervalLattice):
                        evaluation[expr] = fetched.meet(values)
                    else:
                        assert isinstance(values, IndexedLattice)
                        evaluation[expr] = values.refine(fetched)
                else:
                    if isinstance(expr.typ, (SequenceLyraType, DictLyraType)):
                        index = {'_': fetched}
                        idxd = state.lattices[expr.typ](**state.arguments[expr.typ], index=index)
                        evaluation[expr] = idxd
                    else:
                        evaluation[expr] = fetched
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Slicing)
        def visit_Slicing(self, expr: 'Slicing', state=None, evaluation=None):
            raise NotImplementedError   # TODO

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            # TODO: implement properly
            evaluated = evaluation
            evaluated = self.visit(expr.start, state, evaluated)
            sub = BinaryArithmeticOperation.Operator.Sub
            one = Literal(expr.stop.typ, '1')
            stop = BinaryArithmeticOperation(expr.stop.typ, expr.stop, sub, one)
            evaluated = self.visit(stop, state, evaluated)

            if not evaluated[expr.start].is_bottom() and not evaluated[stop].is_bottom():
                lower = evaluated[expr.start].lower
                upper = evaluated[stop].upper
                assert isinstance(expr.typ, ListLyraType)
                value = state.lattices[expr.typ.typ](lower=lower, upper=upper)
                evaluation[expr] = value
            else:
                evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_CastOperation)
        def visit_CastOperation(self, expr: CastOperation, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            container = isinstance(expr.expression.typ, (SequenceLyraType, ContainerLyraType))
            string = isinstance(expr.expression.typ, StringLyraType)
            ensemble = isinstance(expr.expression.typ, SetLyraType)
            dictionary = isinstance(expr.expression.typ, DictLyraType)
            if isinstance(expr.typ, BooleanLyraType) and container:
                current: IndexedLattice = evaluated[expr.expression]
                if current.is_empty():
                    value = state.lattices[expr.typ](**state.arguments[expr.typ]).false()
                elif current.is_nonempty():
                    value = state.lattices[expr.typ](**state.arguments[expr.typ]).true()
                else:
                    value = state.lattices[expr.typ](**state.arguments[expr.typ]).maybe()
                evaluation[expr] = value
            elif isinstance(expr.typ, (IntegerLyraType, FloatLyraType)) and string:
                current: IndexedLattice = evaluated[expr.expression]
                if isinstance(current, IntervalLattice):
                    evaluation[expr] = deepcopy(current)
                else:
                    evaluation[expr] = current.summarize()
            elif isinstance(expr.typ, StringLyraType):
                value = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                evaluation[expr] = value
            elif isinstance(expr.typ, (ListLyraType, TupleLyraType)) and ensemble:
                current: IntervalLattice = deepcopy(evaluated[expr.expression])
                indexed = {'_': current}
                value = state.lattices[expr.typ](**state.arguments[expr.typ], index=indexed)
                evaluation[expr] = value
            elif isinstance(expr.typ, (ListLyraType, SetLyraType, TupleLyraType)) and dictionary:
                current = deepcopy(evaluated[KeysIdentifier(expr.expression)])
                if isinstance(current, IntervalLattice):
                    indexed = {'_': current}
                    value = state.lattices[expr.typ](**state.arguments[expr.typ], index=indexed)
                    evaluation[expr] = value
                else:
                    assert isinstance(current, IndexedLattice)
                    evaluation[expr] = current
            else:   # default case
                evaluation[expr] = deepcopy(evaluated[expr.expression])
            return evaluation

    _evaluation = ExpressionEvaluation()

    # expression refinement

    class ExpressionRefinement(BasisWithSummarization.ExpressionRefinement):

        def visit_Subscription(self, expr, evaluation=None, value=None, state=None):
            refined = deepcopy(evaluation[expr]).meet(value)
            if isinstance(expr.target, VariableIdentifier):
                target = state.store[expr.target]
                _key: List[str] = state._key.visit(expr.key, target.bound, state)
                if len(_key) == 1 and _key[0] != target.default:
                    state.store[expr.target][_key[0]] = refined
                    if expr.target.is_dictionary:
                        summary = state.store[expr.target].summarize()
                        values = expr.target.values
                        if isinstance(state.values[values], IntervalLattice):
                            state.values[values] = state.values[values].meet(summary)
                        else:
                            assert isinstance(state.values[values], IndexedLattice)
                            state.values[values] = state.values[values].refine(summary)
            return state

        def visit_Slicing(self, expr: 'Slicing', evaluation=None, value=None, state=None):
            raise NotImplementedError  # TODO

    _refinement = ExpressionRefinement()


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
        result = '; '.join('{}: {}'.format(var(i), itv(i)) for i in range(env.intdim))
        result += '; '.join(
            '{} -> {}'.format(var(env.intdim + i), itv(env.intdim + i)) for i in range(env.realdim)
        )
        return result.replace('.0', '')

    manager: PyManager = PyBoxMPQManager()
