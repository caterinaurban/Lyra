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
        result = left / right
        if result == inf or result == -inf:
            return left / right
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
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        self.lower = lower
        self.upper = upper
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
            result_left = None
            result_right = None
            # Addition
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return deepcopy(l).meet(result_value.sub(r))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return deepcopy(r).meet(result_value.sub(l))
                if isinstance(expr.left, Operation):
                    left_result_value = deepcopy(result_value).sub(r)
                    result_left = self.visit_inverse(expr.left, interval_store, left_result_value, var_to_substitute, *args, **kwargs)
                if isinstance(expr.right, Operation):
                    right_result_value = deepcopy(result_value).sub(l)
                    result_right = self.visit_inverse(expr.right, interval_store, right_result_value, var_to_substitute, *args, **kwargs)
            # Substraction
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return deepcopy(l).meet(result_value.add(r))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return deepcopy(r).meet(l.sub(result_value))
                if isinstance(expr.left, Operation):
                    left_result_value = deepcopy(result_value).add(r)
                    result_left = self.visit_inverse(expr.left, interval_store, left_result_value, var_to_substitute, *args, **kwargs)
                if isinstance(expr.right, Operation):
                    right_result_value = l.sub(result_value)
                    result_right = self.visit_inverse(expr.right, interval_store, right_result_value, var_to_substitute, *args, **kwargs)
            # Multiplication
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return deepcopy(l).meet(result_value.div(r))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return deepcopy(r).meet(result_value.div(l))
                if isinstance(expr.left, Operation):
                    left_result_value = deepcopy(result_value).div(r)
                    result_left = self.visit_inverse(expr.left, interval_store, left_result_value, var_to_substitute, *args, **kwargs)
                if isinstance(expr.right, Operation):
                    right_result_value = result_value.div(l)
                    result_right = self.visit_inverse(expr.right, interval_store, right_result_value, var_to_substitute, *args, **kwargs)
            # Division
            elif expr.operator == BinaryArithmeticOperation.Operator.Div:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return deepcopy(l).meet(result_value.mult(r))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    if result_value.lower == 0 and result_value.upper == 0:
                        return deepcopy(r).bottom()
                    return deepcopy(r).meet(l.div(result_value))
                if isinstance(expr.left, Operation):
                    left_result_value = deepcopy(result_value).mult(r)
                    result_left = self.visit_inverse(expr.left, interval_store, left_result_value, var_to_substitute, *args, **kwargs)
                if isinstance(expr.right, Operation):
                    right_result_value = deepcopy(l).div(result_value)
                    result_right = self.visit_inverse(expr.right, interval_store, right_result_value, var_to_substitute, *args, **kwargs)
            else:
                raise ValueError(f"Binary operator '{str(expr.operator)}' is not supported!")
            if result_left is not None:
                if result_right is not None:
                    return result_left.meet(result_right)
                else:
                    return result_left
            elif result_right is not None:
                return result_right

        def visit_UnaryArithmeticOperation(self, expr: UnaryArithmeticOperation, *args, **kwargs):
            r = self.visit(expr.expression, *args, **kwargs)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return r
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                return r.negate()
            else:
                raise ValueError(f"Unary Operator {expr.operator} is not supported!")

        def visit_inverse_UnaryArithmeticOperation(self, expr: UnaryArithmeticOperation, interval_store, result_value, var_to_substitute, *args, **kwargs):
            if isinstance(expr.expression, VariableIdentifier) and expr.expression == var_to_substitute:
                if expr.operator == UnaryArithmeticOperation.Operator.Add:
                    return result_value
                elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                    return result_value.negate()
                else:
                    raise ValueError(f"Unary Operator {expr.operator} is not supported!")
            if isinstance(expr.expression, Operation):
                if expr.operator == UnaryArithmeticOperation.Operator.Sub:
                    result_value.negate()
                return self.visit_inverse(expr.expression,  interval_store, result_value, var_to_substitute, *args, **kwargs)

        def visit_BinaryComparisonOperation(self, expr: BinaryComparisonOperation, interval_store, var_to_substitute, *args, **kwargs):
            l = self.visit(expr.left, interval_store, *args, **kwargs)
            r = self.visit(expr.right, interval_store, *args, **kwargs)
            if expr.operator == BinaryComparisonOperation.Operator.Eq:
                result = l.meet(r)
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return result
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return result
                else:
                    raise NotImplementedError(f"Binary operator '{str(expr.operator)}' only supports comparison to a Variable!")
            elif expr.operator == BinaryComparisonOperation.Operator.LtE:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return deepcopy(l).meet(IntervalLattice(-inf, r.upper))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return r.meet(IntervalLattice(l.lower, inf))
                else:
                    raise NotImplementedError(f"Binary operator '{str(expr.operator)}' only supports comparison to a Variable!")
            elif expr.operator == BinaryComparisonOperation.Operator.GtE:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return l.meet(IntervalLattice(r.lower, inf))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return deepcopy(r).meet(IntervalLattice(-inf, l.upper))
                else:
                    raise NotImplementedError(f"Binary operator '{str(expr.operator)}' only supports comparison to a Variable!")
            elif expr.operator == BinaryComparisonOperation.Operator.Lt:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return deepcopy(l).meet(IntervalLattice(-inf, r.upper-1))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return r.meet(IntervalLattice(l.lower+1, inf))
                else:
                    raise NotImplementedError(f"Binary operator '{str(expr.operator)}' only supports comparison to a Variable!")
            elif expr.operator == BinaryComparisonOperation.Operator.Gt:
                if isinstance(expr.left, VariableIdentifier) and expr.left == var_to_substitute:
                    return l.meet(IntervalLattice(r.lower+1, inf))
                elif isinstance(expr.right, VariableIdentifier) and expr.right == var_to_substitute:
                    return deepcopy(r).meet(IntervalLattice(-inf, l.upper-1))
                else:
                    raise NotImplementedError(f"Binary operator '{str(expr.operator)}' only supports comparison to a Variable!")
            else:
                raise NotImplementedError(f"Binary operator '{str(expr.operator)}' is not supported!")

        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_Literal(self, expr: Literal, *args, **kwargs):
            if expr.typ == int:
                c = int(expr.val)
                return IntervalLattice(c, c)
            else:
                raise ValueError(f"Literal type {expr.typ} is not supported!")

        # TODO implement
        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_Index(self, expr: Index, *args, **kwargs):
            raise ValueError(f"Index is not supported!")

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
            for variable in condition.left.ids():  # substitute values on the left side
                value_before = deepcopy(self.store[variable])
                result = IntervalDomain._visitor.visit(condition, self, variable)
                self.store[variable] = value_before.meet(result)
            for variable in condition.right.ids():  # substitute values on the right side
                value_before = deepcopy(self.store[variable])
                result = IntervalDomain._visitor.visit(condition, self, variable)
                self.store[variable] = value_before.meet(result)
        #else:
           # raise NotImplementedError(f"Condition operator '{str(condition.operator)}' is not supported!")
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
                if left not in right_variables:
                    self.store[left] = IntervalLattice().top()
            else:
                self.store[left] = IntervalLattice().top()
                for variable in right_variables:  # substitute values on the right side
                    value_before = deepcopy(self.store[variable])
                    right_value = IntervalDomain._visitor.visit_inverse(right, self, deepcopy(left_value_before), variable)
                    if not value_before.is_bottom():
                        self.store[variable] = value_before.meet(right_value)
                    else:
                        self.store[variable] = right_value
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
