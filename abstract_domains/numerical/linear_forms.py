from abstract_domains.numerical.interval_domain import IntervalLattice
from core.expressions import *

from core.expressions_tools import ExpressionVisitor, PLUS, MINUS
from core.special_expressions import VariadicArithmeticOperation


class InvalidFormError(ValueError):
    pass


class LinearForm:
    """Holds an expression in linear form with one or several variables: `+/- var1 +/- var2 + ... + interval`."""

    def __init__(self, var_summands=None, interval=None):
        """Initializes this instance with the linear form of an expression.

        If possible, this instance holds the parts of the linear form separately. If not possible to 
        construct this form, this raises a InvalidFormError.
        """
        self._var_summands = var_summands or {}  # dictionary holding {var: sign}
        self._interval = interval or IntervalLattice(0, 0)
        self._interval_set = False

    @staticmethod
    def from_expression(expr: Expression):
        form = LinearForm()
        LinearForm._visitor.visit(expr, form)
        return form

    @property
    def var_summands(self):
        return self._var_summands

    def encounter_new_var(self, var, sign=PLUS):
        if var in self.var_summands:
            raise InvalidFormError(f"VariableIdentifier {var} appears twice!")
        self.var_summands[var] = sign

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value

    def encounter_interval(self, interval):
        if self._interval_set:
            raise InvalidFormError("interval set twice (is immutable)!")
        self.interval = interval

    def __eq__(self, other: 'LinearForm'):
        return isinstance(other, self.__class__) \
               and set(self.var_summands.keys()) == set(other.var_summands.keys()) \
               and all([self.var_summands[key] == other.var_summands[key] for key in self.var_summands.keys()]) \
               and self.interval == other.interval

    def __ne__(self, other: 'LinearForm'):
        return not (self == other)

    def __lt__(self, other):
        """Syntactic comparision of this linear form."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.var_summands == other.var_summands \
               and self.interval < other.interval

    def __le__(self, other):
        """Syntactic comparision of this linear form."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.var_summands == other.var_summands \
               and self.interval <= other.interval

    def __gt__(self, other):
        """Syntactic comparision of this linear form."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.var_summands == other.var_summands \
               and self.interval > other.interval

    def __ge__(self, other):
        """Syntactic comparision of this linear form."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.var_summands == other.var_summands \
               and self.interval >= other.interval

    def __hash__(self):
        return hash(repr(self))

    def __str__(self):
        vars_string = ' '.join([f"{str(sign)}{var}" for var, sign in self.var_summands.items()])
        interval_string = f"{self._interval}" if self._interval != LinearForm.zero_interval or not vars_string else ""
        if vars_string and interval_string:
            return f"{vars_string} + {interval_string}"
        else:
            return vars_string or interval_string

    zero_interval = IntervalLattice(0, 0)

    class Visitor(ExpressionVisitor):
        """A visitor to generate a single variable linear form."""

        def __init__(self):
            self._interval_set = False

        # the visit methods should either set parts of the linear form or call visit method on children, propagating if
        # the sub-expressions is negated. They can also fallback on other visitors like the interval visitor via
        # IntervalLattice.evaluate(expr)

        def visit_Literal(self, expr: Literal, linear_form, invert=False):
            linear_form.encounter_interval(IntervalLattice.evaluate(expr))
            if invert:
                linear_form.interval.negate()

        def visit_VariableIdentifier(self, expr: VariableIdentifier, linear_form, invert=False):
            linear_form.encounter_new_var(expr, sign=MINUS if invert else PLUS)

        def visit_Input(self, _: Input, linear_form, invert=False):
            linear_form.encounter_interval(IntervalLattice().top())
            if invert:
                linear_form.interval.negate()

        def visit_BinaryArithmeticOperation(self, expr: BinaryArithmeticOperation, linear_form, invert=False):
            # we have to check if binary operation can be reordered to correspond to valid formats:
            # +/- var + interval
            # OR
            # +/- var1 +/- var2

            try:
                # just try if interval lattice is capable of reducing to single interval (if no vars inside expr)
                linear_form.encounter_interval(IntervalLattice.evaluate(expr.left))
                if invert:
                    linear_form.interval.negate()
            except ValueError:
                self.visit(expr.left, linear_form, invert=invert)

            if expr.operator not in [BinaryArithmeticOperation.Operator.Add, BinaryArithmeticOperation.Operator.Sub]:
                raise InvalidFormError("Unsupported binary arithmetic operator")

            try:
                # just try if interval lattice is capable of reducing to single interval (if no vars inside expr)
                linear_form.encounter_interval(IntervalLattice.evaluate(expr.right))
                if (expr.operator == BinaryArithmeticOperation.Operator.Sub) != invert:
                    linear_form.interval.negate()
            except ValueError:
                self.visit(expr.right, linear_form,
                           invert=(expr.operator == BinaryArithmeticOperation.Operator.Sub) != invert)

        def visit_UnaryArithmeticOperation(self, expr: UnaryArithmeticOperation, linear_form, invert=False):
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                self.visit(expr.expression, linear_form, invert=invert)
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                self.visit(expr.expression, linear_form, invert=not invert)
            else:
                raise ValueError("Unknown operator")

        def visit_VariadicArithmeticOperation(self, expr: VariadicArithmeticOperation, linear_form, invert=False):
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                for e in expr.operands:
                    self.visit(e, linear_form, invert=invert)
            else:
                raise ValueError("Unsupported operator")

        def generic_visit(self, expr, *args, **kwargs):
            raise InvalidFormError(
                f"{type(self)} does not support generic visit of expressions! "
                f"Define handling for expression {type(expr)} explicitly!")

    _visitor = Visitor()  # static class member shared between all instances


class VarForm(LinearForm):
    """Holds an expression in linear form with a single variable: ``+/- var + interval``."""

    def __init__(self, var_sign=None, var=None, interval=None):
        """Initializes this instance with the single variable form of an expression.

        If possible, this instance holds the parts of the single variable linear form separately. If not possible to 
        construct this form, this raises a InvalidFormError.
        """
        super().__init__({var: var_sign} if var_sign and var else None, interval)

    @staticmethod
    def from_expression(expr: Expression):
        form = VarForm()
        LinearForm._visitor.visit(expr, form)

        if len(form.var_summands) > 1:
            raise InvalidFormError("More than a single variable detected!")

        return form

    @property
    def var_sign(self):
        return list(self.var_summands.values())[0] if self.var_summands else PLUS

    @property
    def var(self):
        return list(self.var_summands.keys())[0] if self.var_summands else None

    @var.setter
    def var(self, value):
        self._var_summands.clear()
        if value:  # do only set if not None
            self._var_summands[value] = PLUS
