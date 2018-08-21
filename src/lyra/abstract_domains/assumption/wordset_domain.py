"""
Word Set Abstract Domain
========================

Non-relational abstract domain to be used for **input data assumption analysis**.
The set of possible string values of a program variable in a program state
is represented exactly, up to a certain cardinality.

:Author: Caterina Urban
"""
from collections import defaultdict
from typing import Set

from lyra.abstract_domains.assumption.assumption_domain import JSONMixin, InputMixin
from lyra.abstract_domains.string.stringset_domain import StringSetLattice, StringSetState
from lyra.core.expressions import VariableIdentifier, Expression
from lyra.core.utils import copy_docstring


class WordSetLattice(StringSetLattice, JSONMixin):
    """Word set lattice.

    The default abstraction is ``⊤``,
    which represents all possible string values.
    The bottom element of the lattice is the empty set of strings.

    .. document private methods
    .. automethod:: StringSetLattice._less_equal
    .. automethod:: StringSetLattice._meet
    .. automethod:: StringSetLattice._join
    .. automethod:: StringSetLattice._widening
    .. automethod:: StringSetLattice._concat
    """

    @copy_docstring(JSONMixin.to_json)
    def to_json(self) -> dict:
        return {'strings': list(self.strings)}

    @staticmethod
    @copy_docstring(JSONMixin.from_json)
    def from_json(json: dict) -> 'JSONMixin':
        return WordSetLattice(set(json['strings']))


class WordSetState(StringSetState, InputMixin):
    """Word set analysis state. An element of the word set abstract domain.

    Map from each program variable to the set of its possible string values.
    The default abstraction is the set of all possible string values.

    When reading input data, the corresponding range assumptions
    are stored in the class member ``inputs``, which is a map from each program point
    to the list of range assumptions on the input data read at that point.

    .. document private methods
    .. automethod:: WordSetState._assume
    .. automethod:: WordSetState._substitute
    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: InputMixin = None):
        lattices = defaultdict(lambda: WordSetLattice)
        super(StringSetState, self).__init__(variables, lattices)
        InputMixin.__init__(self, precursory)

    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'WordSetState':
        # collect the new variables appearing in the replacing expression
        variables: Set[VariableIdentifier] = set()
        for identifier in expression.ids():
            if isinstance(identifier, VariableIdentifier):
                variables.add(identifier)
        variables: Set[VariableIdentifier] = variables.difference(set(self.variables))
        if variables:  # if there are new variables appearing in the replacing expression...
            # add the new variables to the current state
            for var in variables:
                self.variables.append(var)
                self.store[var] = self.lattices[type(var.typ)](**self.arguments[type(var.typ)])
            # replace the given variable with the given expression
            self._substitute(variable, expression)
        return self

    def unify(self, other: 'WordSetState') -> 'WordSetState':
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

    class ExpressionRefinement(StringSetState.ExpressionRefinement):

        @copy_docstring(StringSetState.ExpressionRefinement.visit_Input)
        def visit_Input(self, expr, evaluation=None, value=None, state=None):
            state.record(value)
            return state    # nothing to be done

    _refinement = ExpressionRefinement()  # static class member shared between instances
