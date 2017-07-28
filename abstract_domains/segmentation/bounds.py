from abstract_domains.numerical.interval_domain import IntervalLattice
from abstract_domains.numerical.linear_forms import SingleVarLinearForm, LinearForm, InvalidFormError
from abstract_domains.numerical.octagon_domain import OctagonLattice
from core.expressions import Expression, VariableIdentifier
from core.expressions_tools import MINUS, PLUS


class SingleVarLinearFormWithOctagonalComparison(SingleVarLinearForm):
    """Holds a syntactically and semantically comparable expression in linear form with a single variable: ``+/- var 
    + constant``.
    
    For semantic comparision octagonal constraints are used.
    """

    def __init__(self, var=None, interval=None):
        super().__init__(PLUS, var, interval)

    @staticmethod
    def from_expression(expr: Expression):
        form = SingleVarLinearFormWithOctagonalComparison()
        LinearForm._visitor.visit(expr, form)

        if len(form.var_summands) > 1:
            raise InvalidFormError("More than a single variable detected!")

        return form

    def __hash__(self):
        # TODO is this really what we want? syntactical check for set operations in Limits enough?
        # TODO if sometimes the __eq__ is called by set operation, this leads to semantic checks -> inconsistencies?
        return hash(str(self))

    @property
    def interval(self):
        if not super().interval.is_constant():
            raise InvalidFormError("The interval part of this linear form must be constant.")
        return super().interval

    @interval.setter
    def interval(self, value):
        # set property of superclass
        super(SingleVarLinearFormWithOctagonalComparison, self.__class__).interval.fset(self, value)
        if not value.is_constant():
            raise InvalidFormError("The interval part of this linear form must be constant.")

    @property
    def constant(self):
        return self.interval.lower

    @constant.setter
    def constant(self, value):
        self.interval = (value, value)

    def var_interval(self, octagon: OctagonLattice):
        """Finds the interval for the variable term."""
        if self.var:
            interval = octagon.get_interval(
                self.var)  # already returns fresh copy (that we can modify without risk)
            if self.var_sign == MINUS:
                interval.negate()
            return interval
        else:
            return IntervalLattice(0, 0)

    def eq_octagonal(self, other, octagon: OctagonLattice):
        if super().__eq__(other):  # if syntactic check is sufficient
            return True
        return self.le_octagonal(other, octagon) and other.le_octagonal(self, octagon)

    def ne_octagonal(self, other, octagon: OctagonLattice):
        return not self.eq_octagonal(other, octagon)

    def lt_octagonal(self, other, octagon: OctagonLattice):
        """Syntactic and relational (using octagonal constraints) comparision of this linear form."""
        if super().__lt__(other):  # if syntactic check is sufficient
            return True

        # check if self.var + self.interval < other.var + other.interval
        #          <=> self.var - other.var < -self.interval + other.interval
        if self.var and other.var:
            left = octagon.get_octagonal_constraint(self.var_sign, self.var, -other.var_sign, other.var)
        else:
            # Fallback: use interval of one ore none of the two variables to check inequality
            left = self.var_interval(octagon) - other.var_interval(octagon)

        return left < -self.interval + other.interval

    def le_octagonal(self, other, octagon: OctagonLattice):
        """Syntactic and relational (using octagonal constraints) comparision of this linear form."""
        if super().__le__(other):  # if syntactic check is sufficient
            return True

        # check if self.var + self.interval <= other.var + other.interval
        #          <=> self.var - other.var <= other.interval - self.interval
        if self.var and other.var:
            left = octagon.get_octagonal_constraint(self.var_sign, self.var, -other.var_sign, other.var)
        else:
            # Fallback: use interval of one ore none of the two variables to check inequality
            left = self.var_interval(octagon) - other.var_interval(octagon)

        return left <= -self.interval + other.interval

    def gt_octagonal(self, other, octagon: OctagonLattice):
        """Syntactic and relational (using octagonal constraints) comparision of this linear form."""
        if super().__gt__(other):  # if syntactic check is sufficient
            return True

        # check if self.var + self.interval > other.var + other.interval
        #          <=> -self.var + other.var < self.interval - other.interval
        if self.var and other.var:
            left = octagon.get_octagonal_constraint(-self.var_sign, self.var, other.var_sign, other.var)
        else:
            # Fallback: use interval of one ore none of the two variables to check inequality
            left = -self.var_interval(octagon) + other.var_interval(octagon)

        return left < self.interval - other.interval

    def ge_octagonal(self, other, octagon: OctagonLattice):
        """Syntactic and relational (using octagonal constraints) comparision of this linear form."""
        if super().__ge__(other):  # if syntactic check is sufficient
            return True

        # check if self.var + self.interval >= other.var + other.interval
        #          <=> -self.var + other.var <= self.interval - other.interval
        if self.var and other.var:
            left = octagon.get_octagonal_constraint(-self.var_sign, self.var, other.var_sign, other.var)
        else:
            # Fallback: use interval of one ore none of the two variables to check inequality
            left = -self.var_interval(octagon) + other.var_interval(octagon)

        return left <= self.interval - other.interval

    def substitute_variable(self, var: VariableIdentifier, form: 'SingleVarLinearFormWithOctagonalComparison'):
        if self.var and self.var == var:
            self.var = form.var
            self.interval = self.interval + form.interval

        return self
