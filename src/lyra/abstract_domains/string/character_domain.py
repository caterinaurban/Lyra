"""
Character Inclusion Abstract Domain
===================================

Non-relational abstract domain to be used for **string analysis**.
The set of possible string values of a program variable in a program state
is represented by the set of characters that must and may form the string.

:Authors: Radwa Sherif Abdelbar and Caterina Urban
"""
import string
from collections import defaultdict
from copy import deepcopy

from lyra.abstract_domains.lattice import BottomMixin, StringMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import *
from lyra.core.types import StringLyraType
from lyra.core.utils import copy_docstring


_alphabet = set(string.printable)


class CharacterLattice(BottomMixin, StringMixin):
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

    @copy_docstring(StringMixin.concat)
    def _concat(self, other: 'CharacterLattice') -> 'CharacterLattice':
        """``(c1, m1) + (c2, m2) = (c1 ∪ c2, m1 ∪ m2)``."""
        certainly = self.certainly.union(other.certainly)
        maybe = self.certainly.union(other.certainly)
        return self._replace(type(self)(certainly, maybe))


class CharacterState(Store, State):

    """
        An implementation of the Character Inclusion Domain.

        Maps from every string variable to a tuple of two sets: one set of characters that
        are **certainly** included in the string and a set of characters that are **maybe**
        included in the string. The string cannot contain characters from outside the **maybe**
        set and must contain all characters in **certainly**. Therefore,
        the **certainly** set is a subset of the **maybe** set.

    """

    class ExpressionEvaluation(ExpressionVisitor):

        def visit_Literal(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            if expr.typ == StringLyraType():
                evaluation[expr] = state.lattices[expr.typ](set(expr.val), set(expr.val))
            else:
                evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ])
            return evaluation

        def visit_Input(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ])
            return evaluation

        def visit_VariableIdentifier(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        def visit_LengthIdentifier(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_ListDisplay(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_Range(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_AttributeReference(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_Subscription(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_Slicing(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                evaluated2[expr] = deepcopy(evaluated2[expr.left]).concat(evaluated2[expr.right])
                return evaluated2
            evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ])
            return evaluation

        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    class ExpressionRefinement(ExpressionVisitor):

        def visit_Literal(self, expr: 'Literal', state=None, evaluation=None, value=None):
            return state

        def visit_Input(self, expr: 'Input', state=None, evaluation=None, value=None):
            return state

        def visit_VariableIdentifier(self, expr, state=None, evaluation=None, value=None):
            state.store[expr] = evaluation[expr].meet(value)
            return state

        def visit_LengthIdentifier(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_ListDisplay(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_Range(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_AttributeReference(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_Subscription(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_Slicing(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None, value=None):
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                new_value = state.lattices[expr.typ](maybe=value.maybe)
                refined1 = self.visit(expr.right, state, evaluation, new_value)
                refined2 = self.visit(expr.left, refined1, evaluation, new_value)
                return refined2
            return state

        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None, value=None):
            return state

        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None, value=None):
            return state

    _evaluation = ExpressionEvaluation()
    _refinement = ExpressionRefinement()

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        lattices = defaultdict(lambda: CharacterLattice)
        super().__init__(variables, lattices)
        State.__init__(self, precursory)

    def _assign(self, left: Expression, right: Expression) -> 'State':
        if isinstance(left, VariableIdentifier):
            evaluation = self._evaluation.visit(right, self, dict())
            self.store[left] = evaluation[right]
            return self
        raise NotImplementedError(f"Assignment to {left.__class__.__name__} is unsupported!")

    def _assume(self, condition: Expression) -> 'State':
        if isinstance(condition, UnaryBooleanOperation):
            if condition.operator == UnaryBooleanOperation.Operator.Neg:
                expression = condition.expression
                if isinstance(expression, BinaryComparisonOperation):
                    typ = expression.typ
                    left = expression.left
                    operator = expression.operator.reverse_operator()
                    right = expression.right
                    new_expression = BinaryComparisonOperation(typ, left, operator, right)
                    return self._assume(new_expression)
                elif isinstance(expression, UnaryBooleanOperation):
                    if expression.operator == UnaryBooleanOperation.Operator.Neg:
                        return self._assume(expression.expression)
                elif isinstance(expression, BinaryBooleanOperation):
                    left = expression.left
                    op = UnaryBooleanOperation.Operator.Neg
                    left = UnaryBooleanOperation(left.typ, op, left)
                    operator = expression.operator.reverse_operator()
                    right = expression.right
                    op = UnaryBooleanOperation.Operator.Neg
                    right = UnaryBooleanOperation(right.typ, op, right)
                    typ = expression.typ
                    return self._assume(BinaryBooleanOperation(typ, left, operator, right))
        elif isinstance(condition, BinaryBooleanOperation):
            if condition.operator == BinaryBooleanOperation.Operator.And:
                right = deepcopy(self)._assume(condition.right)
                return self._assume(condition.left).meet(right)
            if condition.operator == BinaryBooleanOperation.Operator.Or:
                right = deepcopy(self)._assume(condition.right)
                return self._assume(condition.left).join(right)
        elif isinstance(condition, BinaryComparisonOperation):
            if condition.operator == BinaryComparisonOperation.Operator.Eq:
                left = condition.left
                right = condition.right
                left_eval = self._evaluation.visit(condition.left, self, dict())
                right_eval = self._evaluation.visit(condition.right, self, dict())
                self._refinement.visit(left, self, left_eval, right_eval[right])
                self._refinement.visit(right, self, right_eval, left_eval[left])
        return self

    def enter_if(self) -> 'State':
        return self

    def exit_if(self) -> 'State':
        return self

    def enter_loop(self) -> 'State':
        return self

    def exit_loop(self) -> 'State':
        return self

    def _output(self, output: Expression) -> 'State':
        return self

    def _substitute(self, left: Expression, right: Expression) -> 'State':
        if isinstance(left, VariableIdentifier):
            left_eval = self._evaluation.visit(left, self, dict())
            right_eval = self._evaluation.visit(right, self, dict())
            self._refinement.visit(right, self, right_eval, left_eval[left])
            self.store[left].top()
        return self
