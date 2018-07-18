"""
Range Abstract Domain
=====================

Non-relational abstract domain to be used for **input data assumption analysis**.
The set of possible values of a program variable in a state is represented as a value range.

:Authors: Caterina Urban and Madelin Schumacher
"""
from collections import defaultdict
from math import inf
from typing import Set
from lyra.abstract_domains.assumption.assumption_domain import InputMixin, JSONMixin
from lyra.abstract_domains.numerical.interval_domain import IntervalState, \
    copy_docstring, Input, IntervalLattice
from lyra.core.expressions import VariableIdentifier, Expression


class RangeLattice(IntervalLattice, JSONMixin):
    """Range lattice. The bottom range represents an empty set of values.

    .. image:: _static/interval.jpg

    The default abstraction is the unbounded range ``[-oo, +oo]``.

    .. document private methods
    .. automethod:: RangeLattice._less_equal
    .. automethod:: RangeLattice._meet
    .. automethod:: RangeLattice._join
    .. automethod:: RangeLattice._widening
    .. automethod:: RangeLattice._neg
    .. automethod:: RangeLattice._add
    .. automethod:: RangeLattice._sub
    .. automethod:: RangeLattice._mult
    """
    @copy_docstring(JSONMixin.to_json)
    def to_json(self) -> str:
        return str(self)

    @staticmethod
    @copy_docstring(JSONMixin.from_json)
    def from_json(json: str) -> 'JSONMixin':
        if json == '⊥':
            return RangeLattice().bottom()
        lower, upper = json[1:-1].split(',')
        lower = int(lower) if lower != '-inf' else -inf
        upper = int(upper) if upper != 'inf' else inf
        return RangeLattice(lower, upper)


class RangeState(IntervalState, InputMixin):
    """Range assumption analysis state. An element of the range assumption abstract domain.

    Map from each program variable to the value range representing its value.
    The value of all program variables is represented by the unbounded range by default.

    When reading input data, the corresponding range assumptions
    are stored in the class member ``inputs``, which is a map
    from each program point to the list of range assumptions on the input data read at that point.

    .. document private methods
    .. automethod:: RangeState._assume
    .. automethod:: RangeState._substitute
    """
    def __init__(self, variables: Set[VariableIdentifier], precursory: InputMixin = None):
        """Map each program variable to the interval representing its value.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: RangeLattice)
        super(IntervalState, self).__init__(variables, lattices)
        InputMixin.__init__(self, precursory)

    @copy_docstring(InputMixin.replace)
    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'RangeState':
        # collect the new variables appearing in the replacing expression
        variables: Set[VariableIdentifier] = set()
        for identifier in expression.ids():
            if isinstance(identifier, VariableIdentifier):
                variables.add(identifier)
        variables: Set[VariableIdentifier] = variables.difference(set(self.variables))
        if variables:   # if there are new variables appearing in the replacing expression...
            # add the new variables to the current state
            for var in variables:
                self.variables.append(var)
                self.store[var] = self.lattices[type(var.typ)](**self.arguments[type(var.typ)])
            # replace the given variable with the given expression
            self._substitute(variable, expression)
        return self

    @copy_docstring(InputMixin.unify)
    def unify(self, other: 'RangeState') -> 'RangeState':
        # collect the variables that differ in the current and other state
        mine = sorted(set(self.variables).difference(set(other.variables)), key=lambda x: x.name)
        theirs = sorted(set(other.variables).difference(set(self.variables)), key=lambda x: x.name)
        # replace the variables in the current state that match those in the other state
        for my_var, their_var in zip(mine, theirs):
            # the replacement only occurs when the matching variables in the other state
            # depend on a program point that is smaller than the program point on which
            # the variables in the current state depend
            if their_var.name < my_var.name:
                self.variables[self.variables.index(my_var)] = their_var
                self.store[their_var] = self.store.pop(my_var)
        # add variables only present in the other state
        for var in theirs[len(mine):]:
            self.variables.append(var)
            self.store[var] = self.lattices[type(var.typ)](**self.arguments[type(var.typ)])
        return self

    # expression refinement

    class ArithmeticExpressionRefinement(IntervalState.ArithmeticExpressionRefinement):

        @copy_docstring(IntervalState.ArithmeticExpressionRefinement.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            state.record(value)
            return state    # nothing to be done

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between instances
