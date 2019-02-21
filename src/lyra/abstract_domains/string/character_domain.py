"""
Character Inclusion Abstract Domain
===================================

Non-relational abstract domain to be used for **string analysis**.
The set of possible string values of a program variable in a program state
is represented by the sets of characters that must and may form the string.

:Authors: Radwa Sherif Abdelbar and Caterina Urban
"""
import string
from collections import defaultdict
from copy import deepcopy

from lyra.abstract_domains.basis import Basis
from lyra.abstract_domains.lattice import BottomMixin, SequenceMixin
from lyra.abstract_domains.state import State
from lyra.core.expressions import *
from lyra.core.types import StringLyraType
from lyra.core.utils import copy_docstring


_alphabet = set(string.printable)


class CharacterLattice(BottomMixin, SequenceMixin):
    """Character inclusion lattice.

    The default abstraction is the unconstraining pair ``(∅, Σ)``,
    where ``Σ`` denotes the entire alphabet.
    The bottom element of the lattice represents a contradiction.

    .. document private methods
    .. automethod:: CharacterLattice._less_equal
    .. automethod:: CharacterLattice._meet
    .. automethod:: CharacterLattice._join
    .. automethod:: CharacterLattice._widening
    .. automethod:: CharacterLattice._concat
    """

    def __init__(self, certainly: Set[str] = set(), maybe: Set[str] = _alphabet):
        super().__init__()
        if certainly.issubset(maybe):   # the must and may sets of characters are in agreement
            self._certainly = certainly
            self._maybe = maybe
        else:   # the must and may sets of characters are in conflict
            self.bottom()

    @classmethod
    def from_literal(cls, literal: Literal) -> 'CharacterLattice':
        if isinstance(literal.typ, StringLyraType):
            return cls(set(literal.val), set(literal.val))
        return cls()

    @property
    def certainly(self):
        """Current set of must characters.

        :return: the current set of must characters if there is no conflict, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        return self._certainly

    @property
    def maybe(self):
        """Current set of may characters.

        :return: the current set of may characters if there is no conflict, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        return self._maybe

    def __repr__(self):
        def do(charset: Set[str]):
            if not charset:
                return "∅"
            elif charset == _alphabet:
                return "Σ"
            charlist = sorted(charset, key=lambda x: x)
            return "{" + ", ".join("'{}'".format(char) for char in charlist) + "}"
        if self.is_bottom():
            return "⊥"
        return "(" + do(self.certainly) + ", " + do(self.maybe) + ")"

    @copy_docstring(BottomMixin.top)
    def top(self):
        """The top lattice element is ``(∅, Σ)``."""
        return self._replace(type(self)())

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        return not self.certainly and self.maybe == _alphabet

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'CharacterLattice') -> bool:
        """``(c1, m1) ⊑ (c2, m2)`` if and only if ``c2 ⊆ c1`` and ``m1 ⊆ m2``."""
        return other.certainly.issubset(self.certainly) and self.maybe.issubset(other.maybe)

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'CharacterLattice') -> 'CharacterLattice':
        """``(c1, m1) ⊔ (c2, m2) = (c1 ∩ c2, m1 ∪ m2)``."""
        certainly = self.certainly.intersection(other.certainly)
        maybe = self.maybe.union(other.maybe)
        return self._replace(type(self)(certainly, maybe))

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'CharacterLattice'):
        """``(c1, m1) ⊓ (c2, m2) = (c1 ∪ c2, m1 ∩ m2)``."""
        certainly = self.certainly.union(other.certainly)
        maybe = self.maybe.intersection(other.maybe)
        if certainly.issubset(maybe):
            return self._replace(type(self)(certainly, maybe))
        return self.bottom()

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'CharacterLattice'):
        """``(c1, m1) ▽ (c2, m2) = (c1, m1) ⊔ (c2, m2)``."""
        return self._join(other)

    # string operations

    @copy_docstring(SequenceMixin.concat)
    def _concat(self, other: 'CharacterLattice') -> 'CharacterLattice':
        """``(c1, m1) + (c2, m2) = (c1 ∪ c2, m1 ∪ m2)``."""
        certainly = self.certainly.union(other.certainly)
        maybe = self.maybe.union(other.maybe)
        return self._replace(type(self)(certainly, maybe))


class CharacterState(Basis):
    """Character inclusion analysis state. An element of the character inclusion abstract domain.

    Map from each program variable to the sets of characters
    that must and may form its possible string values.
    The string value of all program variables is unconstrained by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: CharacterState._assign
    .. automethod:: CharacterState._assume
    .. automethod:: CharacterState._substitute
    """
    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        lattices = defaultdict(lambda: CharacterLattice)
        super().__init__(variables, lattices, precursory=precursory)

    @copy_docstring(Basis._assume)
    def _assume(self, condition: Expression, bwd: bool = False) -> 'CharacterState':
        if isinstance(condition, UnaryBooleanOperation):
            if condition.operator == UnaryBooleanOperation.Operator.Neg:
                expression = condition.expression
                if isinstance(expression, BinaryComparisonOperation):
                    typ = expression.typ
                    left = expression.left
                    operator = expression.operator.reverse_operator()
                    right = expression.right
                    new_expression = BinaryComparisonOperation(typ, left, operator, right)
                    return self._assume(new_expression, bwd=bwd)
                elif isinstance(expression, UnaryBooleanOperation):
                    if expression.operator == UnaryBooleanOperation.Operator.Neg:
                        return self._assume(expression.expression, bwd=bwd)
                elif isinstance(expression, BinaryBooleanOperation):
                    left = expression.left
                    op = UnaryBooleanOperation.Operator.Neg
                    left = UnaryBooleanOperation(left.typ, op, left)
                    operator = expression.operator.reverse_operator()
                    right = expression.right
                    op = UnaryBooleanOperation.Operator.Neg
                    right = UnaryBooleanOperation(right.typ, op, right)
                    typ = expression.typ
                    new_expression = BinaryBooleanOperation(typ, left, operator, right)
                    return self._assume(new_expression, bwd=bwd)
        elif isinstance(condition, BinaryBooleanOperation):
            if condition.operator == BinaryBooleanOperation.Operator.And:
                right = deepcopy(self)._assume(condition.right, bwd=bwd)
                return self._assume(condition.left, bwd=bwd).meet(right)
            if condition.operator == BinaryBooleanOperation.Operator.Or:
                right = deepcopy(self)._assume(condition.right, bwd=bwd)
                return self._assume(condition.left, bwd=bwd).join(right)
        elif isinstance(condition, BinaryComparisonOperation):
            if condition.operator == BinaryComparisonOperation.Operator.Eq:
                left = condition.left
                right = condition.right
                left_eval = self._evaluation.visit(condition.left, self, dict())
                right_eval = self._evaluation.visit(condition.right, self, dict())
                self._refinement.visit(left, left_eval, right_eval[right], self)
                self._refinement.visit(right, right_eval, left_eval[left], self)
        return self

    # expression evaluation

    class ExpressionEvaluation(Basis.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the character lattice."""

        def visit_Literal(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluation[expr] = state.lattices[expr.typ].from_literal(expr)
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances

    # expression refinement

    class ExpressionRefinement(Basis.ExpressionRefinement):

        def visit_BinarySequenceOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                refined = evaluation[expr].meet(value)
                refinement1 = state.lattices[expr.typ](maybe=deepcopy(refined).maybe)
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = state.lattices[expr.typ](maybe=deepcopy(refined).maybe)
                updated2 = self.visit(expr.right, evaluation, refinement2, updated1)
                return updated2
            return super().visit_BinarySequenceOperation(expr, evaluation, value, state)

    _refinement = ExpressionRefinement()  # static class member shared between instances
