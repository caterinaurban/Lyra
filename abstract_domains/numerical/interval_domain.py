from copy import deepcopy

from abstract_domains.store import Store
from abstract_domains.lattice import BottomMixin
from abstract_domains.numerical.numerical import NumericalMixin
from abstract_domains.state import State
from core.expressions import *
from typing import List, Set
from math import inf

from core.expressions_tools import ExpressionVisitor


class Interval:
    def __init__(self, lower=-inf, upper=inf):
        """Create an interval lattice for a single variable.
        """
        super().__init__()
        self._lower = lower
        self._upper = upper

    @property
    def lower(self):
        if self.empty():
            return None
        else:
            return self._lower

    @lower.setter
    def lower(self, b):
        self._lower = b

    @property
    def upper(self):
        if self.empty():
            return None
        else:
            return self._upper

    @upper.setter
    def upper(self, b):
        self._upper = b

    @property
    def interval(self):
        if self.empty():
            return None
        else:
            return self.lower, self.upper

    @interval.setter
    def interval(self, bounds):
        (lower, upper) = bounds
        self.lower = lower
        self.upper = upper

    def empty(self) -> bool:
        return self._lower > self._upper

    def set_empty(self) -> 'Interval':
        self.interval = (1, 0)
        return self

    def __eq__(self, other: 'Interval'):
        return isinstance(other, self.__class__) and repr(self) == repr(other)

    def __ne__(self, other: 'Interval'):
        return not (self == other)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError("Incomparable types!")
        if self.empty() or other.empty():
            raise NotImplementedError("Empty intervals are not comparable!")
        return self.upper < other.lower

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError("Incomparable types!")
        if self.empty() or other.empty():
            raise NotImplementedError("Empty intervals are not comparable!")
        return self.upper <= other.lower

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError(f"Incomparable types: {type(other)} and {type(self.__class__)}")
        if self.empty() or other.empty():
            raise NotImplementedError("Empty intervals are not comparable!")
        return self.lower > other.upper

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError("Incomparable types!")
        if self.empty() or other.empty():
            raise NotImplementedError("Empty intervals are not comparable!")
        return self.lower >= other.upper

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        if self.empty():
            return "∅"
        else:
            return f"[{self.lower},{self.upper}]"

    def add(self, other) -> 'Interval':
        if self.empty() or other.empty():
            return self.set_empty()
        else:
            self.interval = (self.lower + other.lower, self.upper + other.upper)
            return self

    def sub(self, other) -> 'Interval':
        if self.empty() or other.empty():
            return self.set_empty()
        else:
            self.interval = (self.lower - other.upper, self.upper - other.lower)
            return self

    def mult(self, other) -> 'Interval':
        if self.empty() or other.empty():
            return self.set_empty()
        else:
            comb = [self.lower * other.lower, self.lower * other.upper, self.upper * other.lower,
                    self.upper * other.upper]
            self.interval = (min(comb), max(comb))
            return self

    def div(self, other) -> 'Interval':
        if self.empty() or other.empty():
            return self.set_empty()
        elif other.lower == other.upper == 0:
            return self.bottom()
        elif other.lower >= 0:
            comb = [self.safe_div(self.lower, other.lower), self.safe_div(self.lower, other.upper),
                    self.safe_div(self.upper, other.lower), self.safe_div(self.upper, other.upper)]
            self.interval = (min(comb), max(comb))
        elif other.upper <= 0:
            self.interval = Interval(-self.upper, -self.lower).div_rec(Interval(-other.upper, -other.lower)).interval
        else:
            val1 = self.div_rec(Interval(other.lower, 0))
            val2 = self.div_rec(Interval(0, other.upper))
            self.interval = IntervalLattice(val1.lower, val1.upper).join(IntervalLattice(val2.lower, val2.upper)).interval
        return self

    def div_rec(self, other) -> 'Interval':
        if self.empty() or other.empty():
            return self.set_empty()
        elif other.lower == other.upper == 0:
            return IntervalDomain().bottom()
        elif other.lower >= 0:
            comb = [self.safe_div(self.lower, other.lower), self.safe_div(self.lower, other.upper),
                    self.safe_div(self.upper, other.lower), self.safe_div(self.upper, other.upper)]
            return Interval(min(comb), max(comb))
        elif other.upper <= 0:
            return Interval(-self.upper, -self.lower).div_rec(Interval(-other.upper, -other.lower))
        else:
            val1 = self.div_rec(Interval(other.lower, 0))
            val2 = self.div_rec(Interval(0, other.upper))
            return IntervalLattice(val1.lower, val1.upper).join(IntervalLattice(val2.lower, val2.upper)).interval

    def safe_div(self, left, right):
        if left == right == 0:
            return 0
        if right == inf or right == -inf:
            return 0
        if right == 0:
            if left > 0:
                return inf
            else:
                return -inf
        return left // right

    def negate(self) -> 'Interval':
        if self.empty():
            return self
        else:
            self.interval = (-self.upper, -self.lower)
            return self


class IntervalLattice(Interval, BottomMixin):
    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        else:
            return super().__repr__()

    def top(self) -> 'IntervalLattice':
        self.lower = -inf
        self.upper = inf
        return self

    def bottom(self) -> 'IntervalLattice':
        super().bottom()
        self.lower = inf
        self.upper = -inf
        return self

    def is_top(self) -> bool:
        return self._lower == -inf and self._upper == inf

    def is_bottom(self) -> bool:
        # we have to check if interval is empty, or got empty by an operation on this interval
        if self.empty():
            self.bottom()
        return super().is_bottom()

    def _less_equal(self, other: 'IntervalLattice') -> bool:
        # NOTE: do not use less equal operator of plain interval since that has different semantics (every value in
        # interval is less equal than any value in other interval)
        return other.lower <= self.lower and self.upper <= other.upper

    def _meet(self, other: 'IntervalLattice'):
        self.lower = max(self.lower, other.lower)
        self.upper = min(self.upper, other.upper)
        return self

    def _join(self, other: 'IntervalLattice') -> 'IntervalLattice':
        self.lower = min(self.lower, other.lower)
        self.upper = max(self.upper, other.upper)
        return self

    def _widening(self, other: 'IntervalLattice'):
        if other.lower < self.lower:
            self.lower = inf
        if other.upper > self.upper:
            self.upper = inf
        return self

    @classmethod
    def evaluate(cls, expr: Expression):
        """Evaluates an expression without variables, interpreting constants in the interval domain.
        
        If this method encounters any variables, it raises a ``ValueError``."""
        return cls._visitor.visit(expr)

    # noinspection PyPep8Naming
    class Visitor(ExpressionVisitor):
        """A visitor to abstractly evaluate an expression (without variables) in the interval domain."""

        def generic_visit(self, expr, *args, **kwargs):
            raise ValueError(
                f"{type(self)} does not support generic visit of expressions! "
                f"Define handling for expression {type(expr)} explicitly!")

        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_Input(self, _: Input, *args, **kwargs):
            return IntervalLattice().top()

        def visit_BinaryArithmeticOperation(self, expr: BinaryArithmeticOperation, *args, **kwargs):
            l = self.visit(expr.left, *args, **kwargs)
            r = self.visit(expr.right, *args, **kwargs)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                return l.add(r)
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                return l.sub(r)
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                return l.mult(r)
            elif expr.operator == BinaryArithmeticOperation.Operator.Div:
                return l.div(r)
            else:
                raise ValueError(f"Binary operator '{str(expr.operator)}' is not supported!")

        def visit_inverse_BinaryArithmeticOperation(self, expr: BinaryArithmeticOperation, interval_store, result_value, var_to_substitute, *args, **kwargs):
            l = self.visit(expr.left, interval_store, result_value, var_to_substitute, *args, **kwargs)
            r = self.visit(expr.right, interval_store, result_value, var_to_substitute, *args, **kwargs)
            # Addition
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    if l.is_bottom():
                        return result_value.sub(r)
                    else:
                        return deepcopy(l).meet(result_value.sub(r))
                elif isinstance(expr.left, VariableIdentifier) and expr.right == var_to_substitute:
                    if r.is_bottom():
                        return result_value.sub(l)
                    else:
                        return deepcopy(r).meet(result_value.sub(l))
                elif isinstance(expr.left, Operation):
                    left_result_value = result_value.sub(r)
                    return self.visit_inverse(expr.left, interval_store, left_result_value, var_to_substitute, *args, **kwargs)
                elif isinstance(expr.right, Operation):
                    right_result_value = result_value.sub(l)
                    return self.visit_inverse(expr.right, interval_store, right_result_value, var_to_substitute, *args, **kwargs)
            # Substraction
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    if l.is_bottom():
                        return result_value.add(r)
                    else:
                        return deepcopy(l).meet(result_value.add(r))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    if r.is_bottom():
                        return l.sub(result_value)
                    else:
                        return deepcopy(r).meet(l.sub(result_value))
                elif isinstance(expr.left, Operation):
                    left_result_value = result_value.add(r)
                    return self.visit_inverse(expr.left, interval_store, left_result_value, var_to_substitute, *args, **kwargs)
                elif isinstance(expr.right, Operation):
                    right_result_value = l.sub(result_value)
                    return self.visit_inverse(expr.right, interval_store, right_result_value, var_to_substitute, *args, **kwargs)
            # Multiplication
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    if l.is_bottom():
                        return result_value.div(r)
                    else:
                        return deepcopy(l).meet(result_value.div(r))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    if r.is_bottom():
                        return result_value.div(l)
                    else:
                        return deepcopy(r).meet(result_value.div(l))
                elif isinstance(expr.left, Operation):
                    left_result_value = result_value.div(r)
                    return self.visit_inverse(expr.left, interval_store, left_result_value, var_to_substitute, *args, **kwargs)
                elif isinstance(expr.right, Operation):
                    right_result_value = result_value.div(l)
                    return self.visit_inverse(expr.right, interval_store, right_result_value, var_to_substitute, *args, **kwargs)
            # Division
            elif expr.operator == BinaryArithmeticOperation.Operator.Div:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    if l.is_bottom():
                        return result_value.mult(r)
                    else:
                        return deepcopy(l).meet(result_value.mult(r))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return IntervalLattice(0,0)  # Assumption: ZeroDivionError
                elif isinstance(expr.left, Operation):
                    left_result_value = result_value.mult(r)
                    return self.visit_inverse(expr.left, interval_store, left_result_value, var_to_substitute, *args, **kwargs)
                elif isinstance(expr.right, Operation):
                    right_result_value = result_value.mult(l)
                    return self.visit_inverse(expr.right, interval_store, right_result_value, var_to_substitute, *args, **kwargs)

            else:
                raise ValueError(f"Binary operator '{str(expr.operator)}' is not supported!")

        '''def visit_inverse_BinaryComparisonOperation(self, expr: BinaryComparisonOperation, inverval_store, *args, **kwargs):
            l = self.visit(expr.left, inverval_store, *args, **kwargs)
            r = self.visit(expr.right, inverval_store, *args, **kwargs)
            if expr.operator == BinaryComparisonOperation.Operator.Eq:
                return l.meet(r)
            else:
                raise NotImplementedError(f"Binary operator '{str(expr.operator)}' is not supported!")'''

        def visit_UnaryArithmeticOperation(self, expr: UnaryArithmeticOperation, *args, **kwargs):
            r = self.visit(expr.expression, *args, **kwargs)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return r
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                return r.negate()
            else:
                raise ValueError(f"Unary Operator {expr.operator} is not supported!")

        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_Literal(self, expr: Literal, *args, **kwargs):
            if expr.typ == int:
                c = int(expr.val)
                return IntervalLattice(c, c)
            else:
                raise ValueError(f"Literal type {expr.typ} is not supported!")

    _visitor = Visitor()  # static class member shared between all instances


class IntervalDomain(Store, NumericalMixin, State):
    def __init__(self, variables: List[VariableIdentifier]):
        super().__init__(variables, {int: IntervalLattice})

    def forget(self, var: VariableIdentifier):
        self.store[var].top()

    def set_bounds(self, var: VariableIdentifier, lower: int, upper: int):
        self.store[var].lower = lower
        self.store[var].upper = upper

    def get_bounds(self, var: VariableIdentifier):
        return self.store[var].lower, self.store[var].upper

    def set_interval(self, var: VariableIdentifier, interval: IntervalLattice):
        self.store[var].lower = interval.lower
        self.store[var].upper = interval.upper

    def set_lb(self, var: VariableIdentifier, constant):
        self.store[var].lower = constant

    def set_ub(self, var: VariableIdentifier, constant):
        self.store[var].upper = constant

    def evaluate(self, expr: Expression):
        interval = IntervalDomain._visitor.visit(expr, self)
        return interval

    def _access_variable(self, variable: VariableIdentifier) -> Set[Expression]:
        return {variable}

    def _assign_variable(self, left: Expression, right: Expression) -> 'IntervalDomain':
        if isinstance(left, VariableIdentifier):
            if left.typ == int:
                self.store[left] = IntervalDomain._visitor.visit(right, self)
        else:
            raise NotImplementedError("Interval domain does only support assignments to variables so far.")
        return self

    def _assume(self, condition: Expression) -> 'IntervalDomain':
        if isinstance(condition, BinaryComparisonOperation):
            IntervalDomain._visitor.visit(condition.right, self)
            l = IntervalDomain._visitor.visit(condition.left, self)
            r = IntervalDomain._visitor.visit(condition.right, self)
            if condition.operator == BinaryComparisonOperation.Operator.Eq:
                if l.is_bottom():
                    result = r
                elif r.is_bottom():
                    result = l
                else:
                    result = l.meet(r)
                if isinstance(condition.left, VariableIdentifier):
                    self.store[condition.left] = result
                if isinstance(condition.right, VariableIdentifier):
                    self.store[condition.right] = result
            elif condition.operator == BinaryComparisonOperation.Operator.NotEq:
                meet_value = deepcopy(l).meet(r)
                if not meet_value.is_bottom():
                    if isinstance(condition.left, VariableIdentifier):
                        self.store[condition.left] = l.bottom()
                    if isinstance(condition.right, VariableIdentifier):
                        self.store[condition.right] = r.bottom()
            else:
                raise NotImplementedError(f"Binary operator '{str(condition.operator)}' is not supported!")
        elif isinstance(condition, UnaryBooleanOperation) and condition.operator == UnaryBooleanOperation.Operator.Neg:
            if condition.expression.operator == BinaryComparisonOperation.Operator.Eq:
                return self.bottom()
        else:
            raise NotImplementedError(f"Condition operator '{str(condition.operator)}' is not supported!")
        return self

    def _evaluate_literal(self, literal: Expression) -> Set[Expression]:
        return {literal}

    def enter_loop(self):
        return self  # nothing to be done

    def exit_loop(self):
        return self  # nothing to be done

    def enter_if(self):
        return self  # nothing to be done

    def exit_if(self):
        return self  # nothing to be done

    def _output(self, output: Expression) -> 'IntervalDomain':
        return self  # nothing to be done

    def _substitute_variable(self, left: Expression, right: Expression):
        if isinstance(left, VariableIdentifier) and left.typ == int:
            left_value_before = self.store[left]
            right_variables = right.ids()
            if isinstance(right, VariableIdentifier):
                    self.store[right] = self.store[left]
            else:
                self.store[left] = IntervalLattice().top()  # TODO: instead of top use information from forward analysis
                for variable in right_variables:  # substitute values on the right side
                    value_before = deepcopy(self.store[variable])
                    right_value = IntervalDomain._visitor.visit_inverse(right, self, left_value_before, variable)
                    if not value_before.is_bottom():
                        self.store[variable] = deepcopy(value_before).meet(right_value)
                    else:
                        self.store[variable] = right_value
            if left not in right_variables:
                self.store[left] = IntervalLattice().bottom()
        else:
            raise NotImplementedError("Interval domain does only support assignments to variables (type integer).")
        return self

    # noinspection PyPep8Naming
    class Visitor(IntervalLattice.Visitor):
        """A visitor to abstractly evaluate an expression (with variables) in the interval domain."""

        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_VariableIdentifier(self, expr: VariableIdentifier, interval_store, *args, **kwargs):
            if expr.typ == int:
                # copy the lattice element, since evaluation should not modify elements
                return deepcopy(interval_store.store[expr])
            else:
                raise ValueError(f"Variable type {expr.typ} is not supported!")

    _visitor = Visitor()  # static class member shared between all instances
