"""
Interval Abstract Domain
========================

Non-relational abstract domain to be used for **interval analysis**.
The set of possible values of a program variable in a state is represented as an interval.
"""


from copy import deepcopy
from math import inf
from typing import List

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
                self.store[left] = self.eval(right)
            else:
                raise ValueError(f"Variable type {left.typ} is not supported!")
        else:
            raise NotImplementedError(f"Assignment to {left.__class__.__name__} is not supported!")
        return self

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'IntervalState':
        # TODO implement this
        return self

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

    def eval(self, expr: Expression) -> 'IntervalLattice':
        """Evaluation of an expression in the current interval state.

        :param expr: expression to be evaluated
        :return: interval representing the value of the expression in the current state
        """
        evaluated = self._evaluation.visit(expr, self)
        return evaluated.val

    class EvaluatedExpression:
        """Wrapper that adds a value to an expression."""

        def __init__(self, expr: Expression, val: 'IntervalLattice'):
            """Create value wrapper for an expression.

            :param expr: evaluated expression
            :param val: value of the expression
            """
            self._expr = expr
            self._val = val

        @property
        def expr(self):
            return self._expr

        @property
        def val(self):
            return self._val

    # noinspection PyPep8Naming
    class ExpressionEvaluation(ExpressionVisitor):
        """Visitor that performs the evaluation of an expression in the interval lattice."""

        # noinspection PyMethodMayBeStatic
        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None):
            if isinstance(expr.typ, BooleanLyraType):
                if expr.val == "True":
                    return IntervalState.EvaluatedExpression(expr, IntervalLattice(1, 1))
                else:  # expr.val == "False":
                    return IntervalState.EvaluatedExpression(expr, IntervalLattice(0, 0))
            elif isinstance(expr.typ, IntegerLyraType):
                val = int(expr.val)
                return IntervalState.EvaluatedExpression(expr, IntervalLattice(val, val))
            else:
                raise ValueError(f"Literal type {expr.typ} is not supported!")

        # noinspection PyMethodMayBeStatic
        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None):
            if isinstance(expr.typ, BooleanLyraType):
                return IntervalState.EvaluatedExpression(expr, IntervalLattice(0, 1))
            elif isinstance(expr.typ, IntegerLyraType):
                return IntervalState.EvaluatedExpression(expr, IntervalLattice())
            else:
                raise ValueError(f"Input type {expr.typ} is not supported!")

        # noinspection PyMethodMayBeStatic
        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None):
            if isinstance(expr.typ, BooleanLyraType) or isinstance(expr.typ, IntegerLyraType):
                return IntervalState.EvaluatedExpression(expr, deepcopy(state.store[expr]))
            else:
                raise ValueError(f"Variable type {expr.typ} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: 'ListDisplay', state=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: 'AttributeReference', state=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_Slice)
        def visit_Slice(self, expr: 'Slice', state=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_Index)
        def visit_Index(self, expr: 'Index', state=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr: UnaryArithmeticOperation, state=None):
            evaluated = self.visit(expr.expression, state)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                return IntervalState.EvaluatedExpression(expr, deepcopy(evaluated.val).negate())
            else:
                raise ValueError(f"Unary operator '{expr.operator}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', state=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr: BinaryArithmeticOperation, state=None):
            left = self.visit(expr.left, state)
            right = self.visit(expr.right, state)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                return IntervalState.EvaluatedExpression(expr, deepcopy(left.val).add(right.val))
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                return IntervalState.EvaluatedExpression(expr, deepcopy(left.val).sub(right.val))
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                return IntervalState.EvaluatedExpression(expr, deepcopy(left.val).mult(right.val))
            else:
                raise ValueError(f"Binary operator '{str(expr.operator)}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', state=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation', state=None):
            raise ValueError(f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!")

    _evaluation = ExpressionEvaluation()    # static class member shared between all instances

    class ArithmeticExpressionRefinement:
        """Visitor that:

        (1) refines the value of an evaluated arithmetic expression based on a given interval value; and
        (2) modifies the current interval state based on the refined value of the arithmetic expression.
        """
        def visit(self, evaluated, *args, **kwargs):
            """Visit of an evaluated expression."""
            method = 'visit_' + evaluated.expr.__class__.__name__
            if hasattr(self, method):
                return getattr(self, method)(evaluated, *args, **kwargs)
            raise NotImplementedError(
                f"Missing visitor for {evaluated.expr.__class__.__name__} in {self.__class__.__qualname__}!")

        # noinspection PyMethodMayBeStatic
        def visit_Literal(self, evaluated, state=None, value=None):
            """Visit of a literal expression."""
            return state    # nothing to be done

        # noinspection PyMethodMayBeStatic
        def visit_Input(self, evaluated, state=None, value=None):
            """Visit of an input expression."""
            return state    # nothing to be done

        # noinspection PyMethodMayBeStatic
        def visit_VariableIdentifier(self, evaluated, state=None, value=None):
            """Visit of a variable identifier."""
            if isinstance(evaluated.expr.typ, BooleanLyraType) or isinstance(evaluated.expr.typ, IntegerLyraType):
                state.store[evaluated.expr] = evaluated.val.meet(value)
                return state
            else:
                raise ValueError(f"Variable type {evaluated.expr.typ} is not supported!")

        def visit_ListDisplay(self, evaluated, state=None, value=None):
            """Visit of a list display."""
            raise ValueError(f"Refinement for a {evaluated.expr.__class__.__name__} expression is not yet supported!")

        def visit_AttributeReference(self, evaluated, state=None, value=None):
            """Visit of an attribute reference."""
            raise ValueError(f"Refinement for a {evaluated.expr.__class__.__name__} expression is not yet supported!")

        def visit_Slice(self, evaluated, state=None, value=None):
            """Visit of a slice expression."""
            raise ValueError(f"Refinement for a {evaluated.expr.__class__.__name__} expression is not yet supported!")

        def visit_Index(self, evaluated, state=None, value=None):
            """Visit of an index expression."""
            raise ValueError(f"Refinement for a {evaluated.expr.__class__.__name__} expression is not yet supported!")

        def visit_UnaryArithmeticOperation(self, evaluated, state=None, value=None):
            """Visit of a unary arithmetic operation."""

            evaluated = self.visit(expr.expression, state)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                return IntervalState.EvaluatedExpression(expr, deepcopy(evaluated.val).negate())
            else:
                raise ValueError(f"Unary operator '{evaluated.expr.operator}' is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, evaluated, state=None, value=None):
            """Visit of a binary arithmetic operation."""
            if evaluated.expr.operator == BinaryArithmeticOperation.Operator.Add:
                left = self.visit(evaluated.expr.left, state, deepcopy(evaluated.val).sub(evaluated.expr.val)
            
            left = self.visit(expr.left, state)
            right = self.visit(expr.right, state)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                return IntervalState.EvaluatedExpression(expr, deepcopy(left.val).add(right.val))
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                return IntervalState.EvaluatedExpression(expr, deepcopy(left.val).sub(right.val))
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                return IntervalState.EvaluatedExpression(expr, deepcopy(left.val).mult(right.val))
            else:
                raise ValueError(f"Binary operator '{str(evaluated.expr.operator)}' is not supported!")

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between all instances
