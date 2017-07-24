from abstract_domains.numerical.interval_domain import IntervalLattice
from abstract_domains.numerical.linear_forms import SingleVarLinearForm
from core.expressions import Expression
from core.expressions_tools import MINUS


class SingleVarLinearFormWithOctagonalComparison(SingleVarLinearForm):
    """Holds a syntactically and semantically comparable expression in linear form with a single variable: ``+/- var 
    + interval``.
    
    For semantic comparision octagonal constraints are used.
    """

    def __init__(self, expr: Expression, octagon):
        super().__init__(expr)
        self._octagon = octagon

    def __hash__(self):
        # TODO is this really what we want? syntactical check for set operations in Limits enough?
        # TODO if sometimes the __eq__ is called by set operation, this leads to semantic checks -> inconsistencies?
        return hash(str(self))

    @property
    def octagon(self):
        return self._octagon

    @octagon.setter
    def octagon(self, value):
        self._octagon = value

    @property
    def var_interval(self):
        """Finds the interval for the variable term."""
        if self.var:
            interval = self.octagon.get_interval(
                self.var)  # already returns fresh copy (that we can modify without risk)
            if self.var_sign == MINUS:
                interval.negate()
            return interval
        else:
            return IntervalLattice(0, 0)

    def __eq__(self, other):
        return self <= other <= self

    def __lt__(self, other):
        """Syntactic and relational (using octagonal constraints) comparision of this linear form."""
        if super().__lt__(other):  # if syntactic check is sufficient
            return True

        # check if self.var + self.interval < other.var + other.interval
        #          <=> self.var - other.var < -self.interval + other.interval
        if self.var and other.var:
            left = self.octagon.get_octagonal_constraint(self.var_sign, self.var, -other.var_sign, other.var)
        else:
            # Fallback: use interval of one ore none of the two variables to check inequality
            left = self.var_interval - other.var_interval

        return left < -self.interval + other.interval

    def __le__(self, other):
        """Syntactic and relational (using octagonal constraints) comparision of this linear form."""
        if super().__le__(other):  # if syntactic check is sufficient
            return True

        # check if self.var + self.interval <= other.var + other.interval
        #          <=> self.var - other.var <= other.interval - self.interval
        if self.var and other.var:
            left = self.octagon.get_octagonal_constraint(self.var_sign, self.var, -other.var_sign, other.var)
        else:
            # Fallback: use interval of one ore none of the two variables to check inequality
            left = self.var_interval - other.var_interval

        return left <= -self.interval + other.interval

    def __gt__(self, other):
        """Syntactic and relational (using octagonal constraints) comparision of this linear form."""
        if super().__gt__(other):  # if syntactic check is sufficient
            return True

        # check if self.var + self.interval > other.var + other.interval
        #          <=> -self.var + other.var < self.interval - other.interval
        if self.var and other.var:
            left = self.octagon.get_octagonal_constraint(-self.var_sign, self.var, other.var_sign, other.var)
        else:
            # Fallback: use interval of one ore none of the two variables to check inequality
            left = -self.var_interval + other.var_interval

        return left < self.interval - other.interval

    def __ge__(self, other):
        """Syntactic and relational (using octagonal constraints) comparision of this linear form."""
        if super().__ge__(other):  # if syntactic check is sufficient
            return True

        # check if self.var + self.interval >= other.var + other.interval
        #          <=> -self.var + other.var <= self.interval - other.interval
        if self.var and other.var:
            left = self.octagon.get_octagonal_constraint(-self.var_sign, self.var, other.var_sign, other.var)
        else:
            # Fallback: use interval of one ore none of the two variables to check inequality
            left = -self.var_interval + other.var_interval

        return left <= self.interval - other.interval

    def __str__(self):
        form_string = super().__str__()
        octagon_string = self.octagon.__str__()
        return form_string + (f" ({octagon_string})" if not self.octagon.is_top() else "")
