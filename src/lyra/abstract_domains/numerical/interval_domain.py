"""
Interval Abstract Domain
========================

Non-relational abstract domain to be used for **interval analysis**.
The set of possible values of a program variable in a state is represented as an interval.

:Authors: Caterina Urban and Simon Wehrli
"""


from copy import deepcopy
from math import inf
from typing import List, Dict

from lyra.abstract_domains.lattice import BottomMixin
from lyra.abstract_domains.numerical.arithmetic import ArithmeticMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import *

from lyra.core.utils import copy_docstring
from lyra.core.types import BooleanLyraType, IntegerLyraType


class IntervalLattice(BottomMixin, ArithmeticMixin):
    """Interval lattice. The bottom interval represents an empty set.

    .. image:: _static/interval.jpg

    The default abstraction is the unbounded interval [-oo, +oo].

    .. document private methods
    .. automethod:: IntervalLattice._less_equal
    .. automethod:: IntervalLattice._meet
    .. automethod:: IntervalLattice._join
    .. automethod:: IntervalLattice._widening
    """
    def __init__(self, lower=-inf, upper=inf):
        super().__init__()
        if lower <= upper:      # the interval is not empty
            self._lower = lower
            self._upper = upper
        else:                   # the interval is empty
            self.bottom()

    @property
    def lower(self):
        """Current lower bound.

        :return: the current lower bound if the interval is not empty, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        else:
            return self._lower

    @property
    def upper(self):
        """Current upper bound.

        :return: the current upper bound if the interval is not empty, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        else:
            return self._upper

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        else:
            return f"[{self.lower}, {self.upper}]"

    @copy_docstring(BottomMixin.top)
    def top(self) -> 'IntervalLattice':
        """The top lattice element is ``[-oo,+oo]``."""
        self.replace(IntervalLattice())
        return self

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        return self.lower == -inf and self.upper == inf

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'IntervalLattice') -> bool:
        """``[a, b] <= [c, d]`` if and only if ``c <= a`` and ``b <= d``."""
        return other.lower <= self.lower and self.upper <= other.upper

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] \/ [c, d] = [min(a,c), max(b,d)]``."""
        lower = min(self.lower, other.lower)
        upper = max(self.upper, other.upper)
        return self.replace(IntervalLattice(lower, upper))

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] /\ [c, d] = [max(a,c), min(b,d)]``."""
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower <= upper:
            return self.replace(IntervalLattice(lower, upper))
        else:
            return self.bottom()

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] ▽ [c, d] = [(c < a? -oo : a), (b < d? +oo : b)]``."""
        lower = self.lower
        upper = self.upper
        if other.lower < self.lower:
            lower = -inf
        if self.upper < other.upper:
            upper = inf
        return self.replace(IntervalLattice(lower, upper))

    # arithmetic operations

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'IntervalLattice':
        """``- [a, b] = [-b, -a]``."""
        lower = 0 - self.upper
        upper = 0 - self.lower
        return self.replace(IntervalLattice(lower, upper))

    @copy_docstring(ArithmeticMixin._add)
    def _add(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] + [c, d] = [a + c, b + d]``."""
        lower = 0 + self.lower + other.lower
        upper = 0 + self.upper + other.upper
        return self.replace(IntervalLattice(lower, upper))

    @copy_docstring(ArithmeticMixin._sub)
    def _sub(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] - [c, d] = [a - d, b - c]``."""
        lower = 0 + self.lower - other.upper
        upper = 0 + self.upper - other.lower
        return self.replace(IntervalLattice(lower, upper))

    @copy_docstring(ArithmeticMixin._mult)
    def _mult(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] * [c, d] = [min(a*c, a*d, b*c, b*d), max(a*c, a*d, b*c, b*d)]``."""
        ac = 0 if self.lower == 0 or other.lower == 0 else 1 * self.lower * other.lower
        ad = 0 if self.lower == 0 or other.upper == 0 else 1 * self.lower * other.upper
        bc = 0 if self.upper == 0 or other.lower == 0 else 1 * self.upper * other.lower
        bd = 0 if self.upper == 0 or other.upper == 0 else 1 * self.upper * other.upper
        lower = min(ac, ad, bc, bd)
        upper = max(ac, ad, bc, bd)
        return self.replace(IntervalLattice(lower, upper))


class IntervalState(Store, State):
    """Interval analysis state. An element of the interval abstract domain.

    Map from each program variable to the interval representing its value.
    The value of all program variables is represented by the unbounded interval by default.

    .. document private methods
    .. automethod:: IntervalState._assign_variable
    .. automethod:: IntervalState._assume
    .. automethod:: IntervalState._output
    .. automethod:: IntervalState._substitute_variable

    """
    def __init__(self, variables: List[VariableIdentifier]):
        """Map each program variable to the interval representing its value.

        :param variables: list of program variables
        """
        super().__init__(variables, {BooleanLyraType: IntervalLattice, IntegerLyraType: IntervalLattice})

    @copy_docstring(State._access_variable)
    def _access_variable(self, variable: VariableIdentifier) -> Set[Expression]:
        return {variable}

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: Expression, right: Expression) -> 'IntervalState':
        if isinstance(left, VariableIdentifier):
            if isinstance(left.typ, BooleanLyraType) or isinstance(left.typ, IntegerLyraType):
                evaluation: Dict[Expression, IntervalLattice] = self._evaluation.visit(right, self, dict())
                self.store[left] = evaluation[right]
            else:
                raise ValueError(f"Variable type {left.typ} is not supported!")
        else:
            raise NotImplementedError(f"Assignment to {left.__class__.__name__} is not supported!")
        return self

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'IntervalState':
        normal = NegationFreeNormalExpression().visit(condition)
        if isinstance(normal, BinaryBooleanOperation):
            if normal.operator == BinaryBooleanOperation.Operator.And:
                right = deepcopy(self)._assume(normal.right)
                return self._assume(normal.left).meet(right)
            if normal.operator == BinaryBooleanOperation.Operator.Or:
                right = deepcopy(self)._assume(normal.right)
                return self._assume(normal.left).join(right)
        elif isinstance(normal, BinaryComparisonOperation):
            evaluation = self._evaluation.visit(normal.left, self, dict())
            return self._refinement.visit(normal.left, evaluation, IntervalLattice(upper=0), self)
        raise ValueError(f"Assumption of a {normal.__class__.__name__} expression is not supported!")

    @copy_docstring(State._evaluate_literal)
    def _evaluate_literal(self, literal: Expression) -> Set[Expression]:
        return {literal}

    @copy_docstring(State.enter_if)
    def enter_if(self):
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self):
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self):
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self):
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'IntervalState':
        return self  # nothing to be done

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: Expression, right: Expression):
        raise NotImplementedError("Interval domain does not yet support variable substitution.")

    # expression evaluation

    class ExpressionEvaluation(ExpressionVisitor):
        """Visitor that performs the evaluation of an expression in the interval lattice."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation    # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                if expr.val == "True":
                    evaluation[expr] = IntervalLattice(1, 1)
                else:  # expr.val == "False":
                    evaluation[expr] = IntervalLattice(0, 0)
                return evaluation
            elif isinstance(expr.typ, IntegerLyraType):
                val = int(expr.val)
                evaluation[expr] = IntervalLattice(val, val)
                return evaluation
            raise ValueError(f"Literal type {expr.typ} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                evaluation[expr] = IntervalLattice(0, 1)
                return evaluation
            elif isinstance(expr.typ, IntegerLyraType):
                evaluation[expr] = IntervalLattice()
                return evaluation
            raise ValueError(f"Input type {expr.typ} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType) or isinstance(expr.typ, IntegerLyraType):
                evaluation[expr] = deepcopy(state.store[expr])
                return evaluation
            raise ValueError(f"Variable type {expr.typ} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None, evaluation=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None, evaluation=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_Slice)
        def visit_Slice(self, expr: Slice, state=None, evaluation=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_Index)
        def visit_Index(self, expr: Index, state=None, evaluation=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr: UnaryArithmeticOperation, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                evaluated[expr] = deepcopy(evaluated[expr.expression]).negate()
                return evaluated
            else:
                raise ValueError(f"Unary operator '{expr.operator}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr: UnaryBooleanOperation, state=None, evaluation=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr: BinaryArithmeticOperation, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                evaluated2[expr] = deepcopy(evaluated2[expr.left]).add(evaluated2[expr.right])
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                evaluated2[expr] = deepcopy(evaluated2[expr.left]).sub(evaluated2[expr.right])
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                evaluated2[expr] = deepcopy(evaluated2[expr.left]).mult(evaluated2[expr.right])
                return evaluated2
            raise ValueError(f"Binary operator '{str(expr.operator)}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr: BinaryBooleanOperation, state=None, evaluation=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr: BinaryComparisonOperation, state=None, evaluation=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

    _evaluation = ExpressionEvaluation()    # static class member shared between all instances

    class ArithmeticExpressionRefinement(ExpressionVisitor):
        """Visitor that:

        (1) refines the value of an evaluated arithmetic expression based on a given interval value; and
        (2) modifies the current interval state based on the refined value of the arithmetic expression.
        """
        def visit(self, expr: Expression, *args, **kwargs):
            """Visit of an evaluated expression."""
            method = 'visit_' + expr.__class__.__name__
            if hasattr(self, method):
                return getattr(self, method)(expr, *args, **kwargs)
            raise NotImplementedError(
                f"Missing visitor for {expr.__class__.__name__} in {self.__class__.__qualname__}!")

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, evaluation=None, value=None, state=None):
            return state    # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            return state    # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, evaluation=None, value=None, state=None):
            if isinstance(expr.typ, BooleanLyraType) or isinstance(expr.typ, IntegerLyraType):
                state.store[expr] = evaluation[expr].meet(value)
                return state
            raise ValueError(f"Variable type {expr.typ} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, evaluation=None, value=None, state=None):
            raise ValueError(f"Refinement for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, evaluation=None, value=None, state=None):
            raise ValueError(f"Refinement for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_Slice)
        def visit_Slice(self, expr: Slice, evaluation=None, value=None, state=None):
            raise ValueError(f"Refinement for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_Index)
        def visit_Index(self, expr: Index, evaluation=None, value=None, state=None):
            raise ValueError(f"Refinement for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return self.visit(expr.expression, evaluation, value, state)
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                refined = evaluation[expr].meet(value)
                return self.visit(expr.expression, evaluation, IntervalLattice(0, 0).sub(refined), state)
            raise ValueError(f"Unary operator '{expr.operator}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            raise ValueError(f"Refinement for a {expr.__class__.__name__} expression is not expected!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                refined = evaluation[expr].meet(value)
                left = self.visit(expr.left, evaluation, deepcopy(refined).sub(evaluation[expr.right]), state)
                right = self.visit(expr.right, evaluation, deepcopy(refined).sub(evaluation[expr.left]), left)
                return right
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                refined = evaluation[expr].meet(value)
                left = self.visit(expr.left, evaluation, deepcopy(refined).add(evaluation[expr.right]), state)
                right = self.visit(expr.right, evaluation, deepcopy(evaluation[expr.left]).sub(refined), left)
                return right
            raise ValueError(f"Binary operator '{str(expr.operator)}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            raise ValueError(f"Refinement for a {expr.__class__.__name__} expression is not expected!")

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, evaluation=None, value=None, state=None):
            raise ValueError(f"Refinement for a {expr.__class__.__name__} expression is not expected!")

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between all instances
