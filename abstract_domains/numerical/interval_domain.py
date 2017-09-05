from copy import deepcopy
from math import inf
from numbers import Number
from typing import List, Union

from abstract_domains.lattice import BottomMixin
from abstract_domains.numerical.numerical import NumericalMixin
from abstract_domains.state import State
from abstract_domains.store import Store
from core.expressions import *
from core.expressions_tools import ExpressionVisitor


def _auto_convert_numbers(func):
    def func_wrapper(self, other: Union[Number, 'Interval']):
        if isinstance(other, Number):
            other = Interval(other, other)

        return func(self, other)

    return func_wrapper


def _check_types(func):
    def func_wrapper(self, other: 'Interval'):
        if not issubclass(self.__class__, Interval) or not issubclass(other.__class__, Interval):
            return NotImplemented

        return func(self, other)

    return func_wrapper


def _check_non_empty(func):
    def func_wrapper(self, other: 'Interval'):
        if self.empty() or other.empty():
            raise ValueError("Empty intervals are not comparable!")

        return func(self, other)

    return func_wrapper


class Interval:
    def __init__(self, lower=-inf, upper=inf):
        """Create an interval lattice for a single variable.
        """
        super().__init__()
        assert lower is not None and upper is not None
        self._lower = lower
        self._upper = upper

    @staticmethod
    def from_constant(constant):
        interval = Interval(constant, constant)
        return interval

    @property
    def lower(self):
        if self.empty():
            return None
        else:
            return self._lower

    @lower.setter
    def lower(self, b):
        assert b is not None
        self._lower = b

    @property
    def upper(self):
        if self.empty():
            return None
        else:
            return self._upper

    @upper.setter
    def upper(self, b):
        assert b is not None
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
        """Return `True` if this interval is empty."""
        return self._lower > self._upper

    def set_empty(self) -> 'Interval':
        """Set this interval to be empty."""
        self.interval = (1, 0)
        return self

    def finite(self) -> bool:
        """Return `True` if this interval is finite."""
        return not ({self.lower, self.upper} & {-inf, inf})

    def is_constant(self) -> bool:
        """Return `True` if this interval is equal to a single constant (different from infinity)."""
        return self.lower == self.upper

    @_check_types
    def __eq__(self, other: 'Interval'):
        return repr(self) == repr(other)

    @_check_types
    def __ne__(self, other: 'Interval'):
        return not (self == other)

    @_auto_convert_numbers
    @_check_types
    @_check_non_empty
    def __lt__(self, other):
        return self.upper < other.lower

    @_auto_convert_numbers
    @_check_types
    @_check_non_empty
    def __le__(self, other):
        return self.upper <= other.lower

    @_auto_convert_numbers
    @_check_types
    @_check_non_empty
    def __gt__(self, other):
        return self.lower > other.upper

    @_auto_convert_numbers
    @_check_types
    @_check_non_empty
    def __ge__(self, other):
        return self.lower >= other.upper

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        if self.empty():
            return "∅"
        else:
            return f"[{self.lower},{self.upper}]"

    # operators (they mutate self, no copy is made!!)

    @_auto_convert_numbers
    @_check_types
    def add(self, other: Union['Interval', int]) -> 'Interval':
        if self.empty() or other.empty():
            return self.set_empty()
        else:
            self.interval = (self.lower + other.lower, self.upper + other.upper)
            return self

    @_auto_convert_numbers
    @_check_types
    def sub(self, other: Union['Interval', int]) -> 'Interval':
        if self.empty() or other.empty():
            return self.set_empty()
        else:
            self.interval = (self.lower - other.upper, self.upper - other.lower)
            return self

    @_auto_convert_numbers
    @_check_types
    def mult(self, other: Union['Interval', int]) -> 'Interval':
        if self.empty() or other.empty():
            return self.set_empty()
        else:
            comb = [self.lower * other.lower, self.lower * other.upper, self.upper * other.lower,
                    self.upper * other.upper]
            self.interval = (min(comb), max(comb))
            return self

    def negate(self) -> 'Interval':
        if self.empty():
            return self
        else:
            self.interval = (-self.upper, -self.lower)
            return self

    # overload operators (do not mutate self, return a modified copy)

    def __pos__(self):
        copy = deepcopy(self)
        return copy

    def __neg__(self):
        copy = deepcopy(self)
        return copy.negate()

    def __add__(self, other):
        copy = deepcopy(self)
        return copy.add(other)

    def __sub__(self, other):
        copy = deepcopy(self)
        return copy.sub(other)

    def __mul__(self, other):
        copy = deepcopy(self)
        return copy.mult(other)


class IntervalLattice(Interval, BottomMixin):
    @staticmethod
    def from_constant(constant):
        interval_lattice = IntervalLattice(constant, constant)
        return interval_lattice

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        else:
            return super().__repr__()

    def top(self) -> 'IntervalLattice':
        self.lower = -inf
        self.upper = inf
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
        
        If this method encounters any variables, it raises a ``ValueError``.
        """
        return cls._visitor.visit(expr)

    # noinspection PyPep8Naming
    class Visitor(ExpressionVisitor):
        """A visitor to abstractly evaluate an expression (without variables) in the interval domain."""

        def generic_visit(self, expr, *args, **kwargs):
            raise ValueError(
                f"{type(self)} does not support generic visit of expressions! "
                f"Define handling for expression {type(expr)} explicitly!")

        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_Index(self, _: Index, *args, **kwargs):
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
                return l.top()
            else:
                raise ValueError(f"Binary operator '{str(expr.operator)}' is not supported!")

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

        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_Input(self, _: Input, *args, **kwargs):
            return IntervalLattice().top()

        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_ListInput(self, _: ListInput, *args, **kwargs):
            return IntervalLattice().top()

        def visit_ListDisplay(self, expr: ListDisplay, *args, **kwargs):
            # find the big join of the intervals of all items of the list display expression
            intervals = map(lambda item: self.visit(item, *args, **kwargs), expr.items)
            return IntervalLattice().bottom().big_join(intervals)

    _visitor = Visitor()  # static class member shared between all instances


class IntervalDomain(Store, NumericalMixin, State):
    def __init__(self, variables: List[VariableIdentifier]):
        super().__init__(variables, {int: lambda _: IntervalLattice(), list: lambda _: IntervalLattice()})

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
        # TODO implement this
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
        raise NotImplementedError("Interval domain does not yet support variable substitution.")

    # noinspection PyPep8Naming
    class Visitor(IntervalLattice.Visitor):
        """A visitor to abstractly evaluate an expression (with variables) in the interval domain."""

        # noinspection PyMethodMayBeStatic, PyUnusedLocal
        def visit_VariableIdentifier(self, expr: VariableIdentifier, interval_store, *args, **kwargs):
            if expr.typ == int:
                # copy the lattice element, since evaluation should not modify elements
                return deepcopy(interval_store.store[expr])
            else:
                return IntervalLattice().top()

    _visitor = Visitor()  # static class member shared between all instances
