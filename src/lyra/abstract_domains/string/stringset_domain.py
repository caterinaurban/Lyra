"""
String Set Abstract Domain
==========================

Non-relational abstract domain to be used for **string analysis**.
The set of possible string values of a program variable in a program state
is represented exactly, up to a certain cardinality.

:Author: Caterina Urban
"""
from collections import defaultdict
from typing import Set

from lyra.abstract_domains.basis import BasisWithSummarization
from lyra.abstract_domains.lattice import TopMixin, SequenceMixin
from lyra.abstract_domains.numerical.interval_lattice import IntervalLattice
from lyra.abstract_domains.state import State
from lyra.core.expressions import Literal, VariableIdentifier, BinaryComparisonOperation, \
    Subscription, LengthIdentifier
from lyra.core.types import StringLyraType
from lyra.core.utils import copy_docstring


class StringSetLattice(TopMixin, SequenceMixin):
    """String set lattice.

    The default abstraction is ``⊤``,
    which represents all possible string values.
    The bottom element of the lattice is the empty set of strings.

    .. document private methods
    .. automethod:: StringSetLattice._less_equal
    .. automethod:: StringSetLattice._meet
    .. automethod:: StringSetLattice._join
    .. automethod:: StringSetLattice._widening
    .. automethod:: StringSetLattice._concat
    """

    def __init__(self, strings: Set[str] = None):
        super().__init__()
        if strings is not None:
            self._strings = strings
        else:
            self.top()

    @classmethod
    def from_literal(cls, literal: Literal) -> 'StringSetLattice':
        if isinstance(literal.typ, StringLyraType):
            return cls({literal.val})
        return cls()

    @property
    def strings(self):
        """Current set of possible strings.

        :return: the current set of possible strings, ``None`` if the lattice element is top
        """
        if self.is_top():
            return None
        return self._strings

    def __repr__(self):
        if self.is_top():
            return "⊤"
        if not self.strings:
            return "∅"
        stringlist = sorted(self.strings, key=lambda x: x)
        return "{" + ", ".join("'{}'".format(string) for string in stringlist) + "}"

    def bottom(self):
        """The bottom lattice element is ``∅``."""
        return self._replace(type(self)(set()))

    def is_bottom(self) -> bool:
        return self.strings is not None and not self.strings

    def _less_equal(self, other: 'StringSetLattice') -> bool:
        return self.strings.issubset(other.strings)

    def _join(self, other: 'StringSetLattice') -> 'StringSetLattice':
        strings = self.strings.union(other.strings)
        return self._replace(type(self)(strings))

    def _meet(self, other: 'StringSetLattice') -> 'StringSetLattice':
        strings = self.strings.intersection(other.strings)
        return self._replace(type(self)(strings))

    def _widening(self, other: 'StringSetLattice') -> 'StringSetLattice':
        if self.less_equal(other) and other.less_equal(self):
            return self
        return self.top()

    # sequence operations

    def _concat(self, other: 'StringSetLattice') -> 'StringSetLattice':
        if self.is_top():
            return self
        elif other.is_top():
            return self._replace(other)
        strings = set()
        for string1 in self.strings:
            for string2 in other.strings:
                strings.add(string1 + string2)
        return self._replace(type(self)(strings))


class StringSetState(BasisWithSummarization):
    """String set analysis state. An element of the string set abstract domain.

    Map from each program variable to the set of its possible string values.
    The default abstraction is the set of all possible string values.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: StringSetState._assign
    .. automethod:: StringSetState._assume
    .. automethod:: StringSetState._substitute
    """
    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        lattices = defaultdict(lambda: StringSetLattice)
        super().__init__(variables, lattices, precursory=precursory)

    @copy_docstring(BasisWithSummarization._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(BasisWithSummarization._assume_subscription)
    def _assume_subscription(self, condition: Subscription, neg: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        left = condition.left
        right = condition.right
        left_eval = self._evaluation.visit(condition.left, self, dict())
        right_eval = self._evaluation.visit(condition.right, self, dict())
        self._refinement.visit(left, left_eval, right_eval[right], self)
        self._refinement.visit(right, right_eval, left_eval[left], self)
        return self

    @copy_docstring(State._assume_noteq_comparison)
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_lt_comparison)
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_lte_comparison)
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_gt_comparison)
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_gte_comparison)
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_is_comparison)
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    @copy_docstring(State._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'StringSetState':
        return self

    # expression evaluation

    class ExpressionEvaluation(BasisWithSummarization.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the string set lattice."""

        def visit_Literal(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluation[expr] = state.lattices[expr.typ].from_literal(expr)
            if isinstance(expr.typ, StringLyraType):
                evaluation[LengthIdentifier(expr)] = IntervalLattice(len(expr.val), len(expr.val))
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances
