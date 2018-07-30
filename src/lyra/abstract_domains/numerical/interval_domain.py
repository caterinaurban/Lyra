"""
Interval Abstract Domain
========================

Non-relational abstract domain to be used for **interval analysis**.
The set of possible values of a program variable in a state is represented as an interval.

:Authors: Caterina Urban and Simon Wehrli
"""
from collections import defaultdict
from copy import deepcopy
from math import inf

from lyra.abstract_domains.lattice import BottomMixin, ArithmeticMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import *

from lyra.core.utils import copy_docstring
from lyra.core.types import BooleanLyraType, IntegerLyraType, FloatLyraType, ListLyraType


class IntervalLattice(BottomMixin, ArithmeticMixin):
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
        self._replace(IntervalLattice())
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
        return self._replace(IntervalLattice(lower, upper))

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] /\ [c, d] = [max(a,c), min(b,d)]``."""
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower <= upper:
            return self._replace(IntervalLattice(lower, upper))
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
        return self._replace(IntervalLattice(lower, upper))

    # arithmetic operations

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'IntervalLattice':
        """``- [a, b] = [-b, -a]``."""
        lower = 0 - self.upper
        upper = 0 - self.lower
        return self._replace(IntervalLattice(lower, upper))

    @copy_docstring(ArithmeticMixin._add)
    def _add(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] + [c, d] = [a + c, b + d]``."""
        lower = 0 + self.lower + other.lower
        upper = 0 + self.upper + other.upper
        return self._replace(IntervalLattice(lower, upper))

    @copy_docstring(ArithmeticMixin._sub)
    def _sub(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] - [c, d] = [a - d, b - c]``."""
        lower = 0 + self.lower - other.upper
        upper = 0 + self.upper - other.lower
        return self._replace(IntervalLattice(lower, upper))

    @copy_docstring(ArithmeticMixin._mult)
    def _mult(self, other: 'IntervalLattice') -> 'IntervalLattice':
        """``[a, b] * [c, d] = [min(a*c, a*d, b*c, b*d), max(a*c, a*d, b*c, b*d)]``."""
        ac = 0 if self.lower == 0 or other.lower == 0 else 1 * self.lower * other.lower
        ad = 0 if self.lower == 0 or other.upper == 0 else 1 * self.lower * other.upper
        bc = 0 if self.upper == 0 or other.lower == 0 else 1 * self.upper * other.lower
        bd = 0 if self.upper == 0 or other.upper == 0 else 1 * self.upper * other.upper
        lower = min(ac, ad, bc, bd)
        upper = max(ac, ad, bc, bd)
        return self._replace(IntervalLattice(lower, upper))


class IntervalState(Store, State):
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
        super().__init__(variables, lattices)
        State.__init__(self, precursory)

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression) -> 'IntervalState':
        if isinstance(left, VariableIdentifier):
            evaluation = self._evaluation.visit(right, self, dict())
            self.store[left] = evaluation[right]
            return self
        raise NotImplementedError(f"Assignment to {left.__class__.__name__} is unsupported!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'IntervalState':
        normal = NegationFreeNormalExpression().visit(condition)
        if isinstance(normal, VariableIdentifier) and isinstance(normal.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(normal, self, dict())
            return self._refinement.visit(normal, evaluation, IntervalLattice(1, 1), self)
        elif isinstance(normal, UnaryBooleanOperation):
            if normal.operator == UnaryBooleanOperation.Operator.Neg:
                expression = normal.expression
                if isinstance(expression, VariableIdentifier):
                    if isinstance(expression.typ, BooleanLyraType):
                        evaluation = self._evaluation.visit(normal, self, dict())
                        false = IntervalLattice(0, 0)
                        return self._refinement.visit(expression, evaluation, false, self)
        elif isinstance(normal, BinaryBooleanOperation):
            if normal.operator == BinaryBooleanOperation.Operator.And:
                right = deepcopy(self)._assume(normal.right)
                return self._assume(normal.left).meet(right)
            if normal.operator == BinaryBooleanOperation.Operator.Or:
                right = deepcopy(self)._assume(normal.right)
                return self._assume(normal.left).join(right)
        elif isinstance(normal, BinaryComparisonOperation):
            if normal.operator == BinaryComparisonOperation.Operator.Is:
                error = f"Assumption of a comparison with {normal.operator} is unsupported!"
                raise ValueError(error)
            elif normal.operator == BinaryComparisonOperation.Operator.IsNot:
                error = f"Assumption of a comparison with {normal.operator} is unsupported!"
                raise ValueError(error)
            elif normal.operator == BinaryComparisonOperation.Operator.In:
                if isinstance(normal.right, Range):
                    typ = BooleanLyraType()
                    left = normal.left
                    lower_operator = BinaryComparisonOperation.Operator.GtE
                    lower_right = normal.right.start
                    lower = BinaryComparisonOperation(typ, left, lower_operator, lower_right)
                    upper_operator = BinaryComparisonOperation.Operator.Lt
                    upper_right = normal.right.stop
                    upper = BinaryComparisonOperation(typ, left, upper_operator, upper_right)
                    right = deepcopy(self)._assume(upper)
                    return self._assume(lower).meet(right)
            elif normal.operator == BinaryComparisonOperation.Operator.NotIn:
                if isinstance(normal.right, Range):
                    typ = BooleanLyraType()
                    left = normal.left
                    lower_operator = BinaryComparisonOperation.Operator.Lt
                    lower_right = normal.right.start
                    lower = BinaryComparisonOperation(typ, left, lower_operator, lower_right)
                    upper_operator = BinaryComparisonOperation.Operator.GtE
                    upper_right = normal.right.stop
                    upper = BinaryComparisonOperation(typ, left, upper_operator, upper_right)
                    right = deepcopy(self)._assume(upper)
                    return self._assume(lower).join(right)
            evaluation = self._evaluation.visit(normal.left, self, dict())
            return self._refinement.visit(normal.left, evaluation, IntervalLattice(upper=0), self)
        error = f"Assumption of a {normal.__class__.__name__} expression is unsupported!"
        raise ValueError(error)

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

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression):
        if isinstance(left, VariableIdentifier):
            # record the current value of the substituted variable
            value: IntervalLattice = deepcopy(self.store[left])
            # forget the current value of the substituted variable
            self.store[left].top()
            # evaluate the right-hand side proceeding bottom-up using the updated store
            evaluation = self._evaluation.visit(right, self, dict())
            # restrict the value of the right-hand side using that of the substituted variable
            refinement = evaluation[right].meet(value)
            # refine the updated store proceeding top-down on the right-hand side
            self._refinement.visit(right, evaluation, refinement, self)
            return self
        elif isinstance(left, Subscription) or isinstance(left, Slicing):
            # copy the current state
            current: IntervalState = deepcopy(self)
            # perform the substitution on the copy of the current state
            target = left.target
            value: IntervalLattice = deepcopy(current.store[target])
            current.store[target].top()
            evaluation = current._evaluation.visit(right, current, dict())
            refinement = evaluation[right].meet(value)
            current._refinement.visit(right, evaluation, refinement, current)
            # perform a weak update on the current state
            return self.join(current)
        raise NotImplementedError(f"Substitution of {left.__class__.__name__} is unsupported!")

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
            elif isinstance(expr.typ, FloatLyraType):
                val = float(expr.val)
                evaluation[expr] = IntervalLattice(val, val)
                return evaluation
            evaluation[expr] = IntervalLattice()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr: LengthIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target, state, evaluation)
            evaluation[expr] = evaluated[expr.target]
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                evaluation[expr] = IntervalLattice(0, 1)
                return evaluation
            evaluation[expr] = IntervalLattice()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                evaluated[expr] = evaluated[expr.expression]
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                evaluated[expr] = deepcopy(evaluated[expr.expression]).neg()
                return evaluated
            raise ValueError(f"Unary arithmetic operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation    # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                if isinstance(expr.expression.typ, BooleanLyraType):
                    value = evaluated[expr.expression]
                    if value == IntervalLattice(0, 1):
                        evaluated[expr] = IntervalLattice(0, 1)
                        return evaluated
                    elif value == IntervalLattice(1, 1):
                        evaluated[expr] = IntervalLattice(0, 0)
                        return evaluated
                    elif value == IntervalLattice(0, 0):
                        evaluated[expr] = IntervalLattice(1, 1)
                        return evaluated
            raise ValueError(f"Unary boolean operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
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
            raise ValueError(f"Binary arithmetic operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

    _evaluation = ExpressionEvaluation()    # static class member shared between all instances

    # expression refinement

    class ArithmeticExpressionRefinement(ExpressionVisitor):
        """Visitor that:

        (1) refines the value of an evaluated arithmetic expression based on a given interval; and
        (2) modifies the current state based on the refined value of the arithmetic expression.
        """

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, evaluation=None, value=None, state=None):
            return state    # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, evaluation=None, value=None, state=None):
            state.store[expr] = evaluation[expr].meet(value)
            return state

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr, evaluation=None, value=None, state=None):
            state.store[expr] = evaluation[expr].meet(value)
            return state

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, evaluation=None, value=None, state=None):
            state.store[expr.target] = evaluation[expr].meet(value)
            return state

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            return state    # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return self.visit(expr.expression, evaluation, value, state)
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                refined = evaluation[expr].meet(value)
                val = IntervalLattice(0, 0).sub(refined)
                return self.visit(expr.expression, evaluation, val, state)
            raise ValueError(f"Unary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                if isinstance(expr.expression.typ, BooleanLyraType):
                    refined = evaluation[expr].meet(value)
                    if refined == IntervalLattice(0, 1):
                        refinement = IntervalLattice(0, 1)
                        return self.visit(expr.expression, evaluation, refinement, state)
                    elif refined == IntervalLattice(1, 1):
                        refinement = IntervalLattice(0, 0)
                        return self.visit(expr.expression, evaluation, refinement, state)
                    elif refined == IntervalLattice(0, 0):
                        refinement = IntervalLattice(1, 1)
                        return self.visit(expr.expression, evaluation, refinement, state)
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).sub(evaluation[expr.right])
                left = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(refined).sub(evaluation[expr.left])
                right = self.visit(expr.right, evaluation, refinement2, left)
                return right
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).add(evaluation[expr.right])
                left = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(evaluation[expr.left]).sub(refined)
                right = self.visit(expr.right, evaluation, refinement2, left)
                return right
            raise ValueError(f"Binary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between instances
