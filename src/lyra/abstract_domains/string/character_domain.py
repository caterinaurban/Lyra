import string
from copy import deepcopy

from docutils.io import Input

from lyra.abstract_domains.lattice import BottomMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import *
from lyra.core.types import StringLyraType
from lyra.core.utils import copy_docstring

_alphabet = set(string.printable)


class CharacterLattice(BottomMixin):

    def __init__(self, certainly=set(), maybe=_alphabet):
        self._certainly = certainly
        self._maybe = maybe
        super().__init__()
        if not self.certainly.issubset(self.maybe):
            self.bottom()

    @property
    def certainly(self):
        return self._certainly

    @property
    def maybe(self):
        return self._maybe

    def top(self):
        return self._replace(CharacterLattice())

    def __repr__(self):
        if self.is_bottom():
            return "⊥"

        if self.is_top():
            return "T"

        return "(<{}>, <{}>)".format(self.certainly, self.maybe)

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        return not self.is_bottom() and self.certainly == set() and self.maybe == _alphabet

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'CharacterLattice') -> bool:
        return self.maybe.issuperset(other.maybe) and self.certainly.issubset(other.certainly)

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'CharacterLattice') -> 'CharacterLattice':
        maybe = self.certainly.intersection(other.certainly)
        certainly = self.maybe.intersection(other.maybe)
        return self._replace(CharacterLattice(maybe, certainly))

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'CharacterLattice'):
        maybe = self.certainly.union(other.certainly)
        certainly = self.maybe.intersection(other.maybe)
        return self._replace(CharacterLattice(maybe, certainly))

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'CharacterLattice'):
        return self._join(other)

    def concat(self, other: 'CharacterLattice') -> 'CharacterLattice':
        """
            Define semantics for the string concatenation operation.
            Both the **certainly** and **maybe** sets are joined
        :param other: lattice element to be concatenated with the current element
        :return: the result of the concatenation
        """
        certainly = self.certainly.union(other.certainly)
        maybe = self.certainly.union(other.certainly)
        return self._replace(certainly, maybe)


class CharacterState(Store, State):

    """
        An implementation of the Character Inclusion Domain.

        Maps from every string variable to a tuple of two sets: one set of characters that
        are **certainly** included in the string and a set of characters that are **maybe**
        included in the string. The string cannot contain characters from outside the **maybe**
        set and must contain all characters in **certainly**. Therefore,
        the **certainly** set is a subset of the **maybe** set.

    """

    class ConditionEvaluator(ExpressionVisitor):

        def visit_Literal(self, expr, state=None, eval=None):
            if expr.typ == StringLyraType():
                return CharacterLattice(set(expr.val), set(expr.val))
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_Input(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_VariableIdentifier(self, expr, state=None, eval=None):
            return state.store[expr]

        def visit_LengthIdentifier(self, expr):
            pass

        def visit_ListDisplay(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_Range(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_AttributeReference(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_Subscription(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_Slicing(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_UnaryArithmeticOperation(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_UnaryBooleanOperation(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_BinaryArithmeticOperation(self, expr, state=None, eval=None):
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                left = self.visit(expr.left, state, eval)
                right = self.visit(expr.right, state, eval)
                return left.concat(right)
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_BinaryBooleanOperation(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

        def visit_BinaryComparisonOperation(self, expr, state=None, eval=None):
            raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    class Refinement(ExpressionVisitor):

        def visit_Literal(self, expr: 'Literal', state=None, evaluation=None):
            pass

        def visit_Input(self, expr: 'Input', state=None, evaluation=None):
            pass

        def visit_VariableIdentifier(self, expr, state=None, evaluation=None):
            state.store[expr].meet(evaluation)

        def visit_LengthIdentifier(self, expr):
            pass

        def visit_ListDisplay(self, expr, state=None, evaluation=None):
            pass

        def visit_Range(self, expr, state=None, evaluation=None):
            pass

        def visit_AttributeReference(self, expr, state=None, evaluation=None):
            pass

        def visit_Subscription(self, expr, state=None, evaluation=None):
            pass

        def visit_Slicing(self, expr, state=None, evaluation=None):
            pass

        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            pass

        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            pass

        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
            evaluation = CharacterLattice(maybe=evaluation.certainly)
            self.visit(expr.right, state, evaluation)
            self.visit(expr.left, state, evaluation)

        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            pass

        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            pass

    _evaluator = ConditionEvaluator()
    _refinement = Refinement()

    def __init__(self, variables: Set[VariableIdentifier]):
        self._variables = variables
        lattices = {v.typ: CharacterLattice for v in variables}
        super().__init__(variables, lattices)

    def _assign(self, left: Expression, right: Expression) -> 'State':
        raise Exception("Assignment should not be called in backward analysis.")

    def _assume(self, condition: Expression) -> 'State':
        if isinstance(condition, UnaryBooleanOperation):
            if condition.operator == UnaryBooleanOperation.Operator.Neg:
                expression = condition.expression
                if isinstance(expression, BinaryComparisonOperation):
                    left = expression.left
                    operator = expression.operator.reverse_operator()
                    right = expression.right
                    new_expression = BinaryBooleanOperation(expression.typ, left, operator, right)
                    return self._assume(new_expression)
                elif isinstance(expression, UnaryBooleanOperation):
                    if isinstance(expression, UnaryBooleanOperation.Operator.Neg):
                        return self._assume(expression.expression)
                elif isinstance(expression, BinaryBooleanOperation):
                    left = expression.left
                    op = UnaryBooleanOperation.Operator.Neg
                    left = UnaryBooleanOperation(left.typ, op, left)
                    operator = expression.operator.reverse_operator()
                    right = expression.right
                    op = UnaryBooleanOperation.Operator.Neg
                    right = UnaryBooleanOperation(right.typ, op, right)
                    return self._assume(BinaryBooleanOperation(expression.typ, left, operator, right))
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
                try:
                    left_eval = self._evaluator.visit(condition.left, self)
                    right_eval = self._evaluator.visit(condition.right, self)
                except NotImplementedError:
                    return self.meet(deepcopy(self.top()))
                self._refinement.visit(left, self, right_eval)
                self._refinement.visit(right, self, left_eval)
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
        left_eval = self._evaluator.visit(left, self)
        self._refinement.visit(right, self, left_eval)
        self.store[left].top()
        return self
