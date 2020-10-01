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
from typing import Union

from apronpy.box import PyBox, PyBoxMPQManager
from apronpy.manager import PyManager

from lyra.abstract_domains.basis import BasisWithSummarization, Basis, BasisWithIndexing
from lyra.abstract_domains.container.indexed_lattice import IndexedLattice
from lyra.abstract_domains.lattice import SequenceMixin
from lyra.abstract_domains.numerical.apron_domain import APRONStateWithSummarization
from lyra.abstract_domains.numerical.interval_lattice import IntervalLattice
from lyra.abstract_domains.state import State
from lyra.core.expressions import *

from lyra.core.utils import copy_docstring
from lyra.core.types import BooleanLyraType, IntegerLyraType, SequenceLyraType, FloatLyraType


class IntervalStateMixin(Basis):

    @copy_docstring(BasisWithSummarization._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False):
        if isinstance(condition.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(condition, self, dict())
            if self.is_bottom():
                return self
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
        if self.is_bottom():
            return self
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
        if self.is_bottom():
            return self
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
        if self.is_bottom():
            return self
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
        if self.is_bottom():
            return self
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

    @copy_docstring(BasisWithSummarization._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self


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

    @copy_docstring(BasisWithSummarization._assume_subscription)
    def _assume_subscription(self, condition: Subscription, neg: bool = False):
        if isinstance(condition.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(condition, self, dict())
            if self.is_bottom():
                return self
            if neg:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).false()
            else:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).true()
            if not value.less_equal(evaluation[condition.target]):
                return self.bottom()
            return self
        raise ValueError(f"Assumption of variable {condition} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        if condition.forloop and not bwd:  # assumption in a for loop during forward analysis
            top = self.lattices[condition.left.typ](**self.arguments[condition.left.typ]).top()
            left = defaultdict(lambda: top)
        else:  # condition assumption
            left = self._evaluation.visit(condition.left, self, dict())
            if self.is_bottom():
                return self
        right = self._evaluation.visit(condition.right, self, dict())
        if self.is_bottom():
            return self
        return self._refinement.visit(condition.left, left, right[condition.right], self)

    # expression evaluation

    class ExpressionEvaluation(BasisWithSummarization.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the interval lattice."""

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation    # nothing to be done
            evaluation[expr] = state.lattices[expr.typ].from_literal(expr)
            if isinstance(expr.typ, StringLyraType):
                evaluation[LengthIdentifier(expr)] = IntervalLattice(len(expr.val), len(expr.val))
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done

            evaluated = self.visit(expr.start, state, evaluation)
            if state.is_bottom():
                return evaluation
            sub = BinaryArithmeticOperation.Operator.Sub
            one = Literal(expr.stop.typ, '1')
            stop = BinaryArithmeticOperation(expr.stop.typ, expr.stop, sub, one)
            evaluated = self.visit(stop, state, evaluated)
            if state.is_bottom():
                return evaluation

            if not evaluated[expr.start].is_bottom() and not evaluated[stop].is_bottom():
                lower = evaluated[expr.start].lower
                upper = evaluated[stop].upper
                value = state.lattices[expr.typ](lower=lower, upper=upper)
                evaluation[expr] = value
                if lower != -inf and upper != inf:
                    size = len(range(lower, upper + 1))
                    length = IntervalLattice(lower=size, upper=size)
                else:
                    length = IntervalLattice(lower=0)
                evaluation[LengthIdentifier(expr)] = length
            else:
                evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
                evaluation[LengthIdentifier(expr)] = IntervalLattice(lower=0, upper=0)
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances


class IntervalStateWithIndexing(IntervalStateMixin, BasisWithIndexing):
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

    @copy_docstring(BasisWithSummarization._assume_subscription)
    def _assume_subscription(self, condition: Subscription, neg: bool = False):
        if isinstance(condition.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(condition, self, dict())
            if self.is_bottom():
                return self
            if neg:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).false()
            else:
                value = self.lattices[condition.typ](**self.arguments[condition.typ]).true()
            if not value.less_equal(evaluation[condition]):
                return self.bottom()
            return self
        raise ValueError(f"Assumption of variable {condition} is unsupported!")

    @copy_docstring(BasisWithSummarization._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        if condition.forloop and not bwd:  # assumption in a for loop during forward analysis
            top = self.lattices[condition.left.typ](**self.arguments[condition.left.typ]).top()
            left = defaultdict(lambda: top)
        else:  # condition assumption
            left = self._evaluation.visit(condition.left, self, dict())
            if self.is_bottom():
                return self
        evaluated = self._evaluation.visit(condition.right, self, dict())
        if self.is_bottom():
            return self
        right = evaluated[condition.right]
        if isinstance(right, IntervalLattice):
            return self._refinement.visit(condition.left, left, deepcopy(right), self)
        else:
            assert isinstance(right, IndexedLattice)
            if isinstance(condition.right.typ, DictLyraType):
                if isinstance(condition.right, VariableIdentifier):
                    keys = self.keys[condition.right.keys]
                    itv = deepcopy(keys) if isinstance(keys, IntervalLattice) else keys.summarize()
                else:
                    itv = right.summarize(keys=condition.right.typ.key_typ)
                return self._refinement.visit(condition.left, left, itv, self)
            else:
                return self._refinement.visit(condition.left, left, right.summarize(), self)

    # expression evaluation

    class ExpressionEvaluation(BasisWithIndexing.ExpressionEvaluation):

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
            if isinstance(expr.typ, StringLyraType):
                evaluation[LengthIdentifier(expr)] = IntervalLattice(len(expr.val), len(expr.val))
            return evaluation

        @copy_docstring(BasisWithSummarization.ExpressionEvaluation.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.start, state, evaluation)
            if state.is_bottom():
                return evaluation
            sub = BinaryArithmeticOperation.Operator.Sub
            one = Literal(expr.stop.typ, '1')
            stop = BinaryArithmeticOperation(expr.stop.typ, expr.stop, sub, one)
            evaluated = self.visit(stop, state, evaluated)
            if state.is_bottom():
                return evaluation
            if not evaluated[expr.start].is_bottom() and not evaluated[stop].is_bottom():
                lower = evaluated[expr.start].lower
                upper = evaluated[stop].upper
                if lower != -inf and upper != inf:
                    index = dict()
                    for i in range(lower, upper + 1):
                        index[str(i)] = state.lattices[expr.typ.typ](lower=i, upper=i)
                    length = IntervalLattice(lower=len(index), upper=len(index))
                else:
                    index = {'_': state.lattices[expr.typ.typ](lower=lower, upper=upper)}
                    length = IntervalLattice(lower=0)
                value = state.lattices[expr.typ](**state.arguments[expr.typ], index=index)
                evaluation[expr] = value
                evaluation[LengthIdentifier(expr)] = length
            else:
                evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
                evaluation[LengthIdentifier(expr)] = IntervalLattice(lower=0, upper=0)
            return evaluation

    _evaluation = ExpressionEvaluation()


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
