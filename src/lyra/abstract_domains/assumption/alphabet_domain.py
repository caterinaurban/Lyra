"""
Alphabet Abstract Domain
========================

Non-relational abstract domain to be used for **input data assumption analysis**.
The set of possible string values of a program variable in a program state
is represented by the sets of characters that must and may form the string.

:Authors: Radwa Sherif Abdelbar and Caterina Urban
"""

from collections import defaultdict
from typing import Set

from lyra.abstract_domains.assumption.assumption_domain import JSONMixin, InputMixin
from lyra.abstract_domains.string.character_domain import CharacterLattice, CharacterState
from lyra.assumption.error import CheckerError, DependencyError
from lyra.core.expressions import VariableIdentifier, Expression
from lyra.core.utils import copy_docstring


class AlphabetLattice(CharacterLattice, JSONMixin):
    """Alphabet lattice.

    The default abstraction is the unconstraining pair ``(∅, Σ)``,
    where ``Σ`` denotes the entire alphabet.
    The bottom element of the lattice represents a contradiction.

    .. document private methods
    .. automethod:: AlphabetLattice._less_equal
    .. automethod:: AlphabetLattice._meet
    .. automethod:: AlphabetLattice._join
    .. automethod:: AlphabetLattice._widening
    .. automethod:: AlphabetLattice._concat
    """

    @copy_docstring(JSONMixin.to_json)
    def to_json(self) -> dict:
        return {'certainly': list(self.certainly), 'maybe': list(self.maybe)}

    @staticmethod
    def from_json(json: dict) -> 'JSONMixin':
        return AlphabetLattice(set(json['certainly']), set(json['maybe']))

    def check_input(self,  pp: VariableIdentifier, pp_value: dict, line_errors: dict):
        if self.is_top():
            return
        input_line = pp_value[pp][0]
        input_value = pp_value[pp][1]
        if input_value is not None:
            input_value = set(input_value)
            error_message = ""
            if not input_value.issuperset(self.certainly):
                s = ', '.join(['\'' + c + '\'' for c in sorted(self.certainly)])
                error_message += "This value must contain *all* the characters: {}".format(s)

            if not input_value.issubset(self.maybe):
                if len(error_message) > 0:
                    error_message += "; \n"
                s = ', '.join(['\'' + c + '\'' for c in sorted(self.maybe)])
                error_message += "This value is allowed to contain only the characters: {}"\
                    .format(s)
            if len(error_message) > 0:
                error = CheckerError(error_message)
                line_errors[input_line].append(error)
        else:
            error = DependencyError(input_line)
            line_errors[input_line].append(error)


class AlphabetState(CharacterState, InputMixin):
    """Alphabet analysis state. An element of the alphabet abstract domain.

    Map from each program variable to the sets of characters
    that must and may form its possible string values.
    The string value of all program variables is unconstrained by default.

    When reading input data, the corresponding range assumptions
    are stored in the class member ``inputs``, which is a map from each program point
    to the list of range assumptions on the input data read at that point.

    .. document private methods
    .. automethod:: AlphabetState._assume
    .. automethod:: AlphabetState._substitute
    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: InputMixin = None):
        lattices = defaultdict(lambda: AlphabetLattice)
        super(CharacterState, self).__init__(variables, lattices)
        InputMixin.__init__(self, precursory)

    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'AlphabetState':
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

    def unify(self, other: 'AlphabetState') -> 'AlphabetState':
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

    class ExpressionRefinement(CharacterState.ExpressionRefinement):

        @copy_docstring(CharacterState.ExpressionRefinement.visit_Input)
        def visit_Input(self, expr, evaluation=None, value=None, state=None):
            state.record(value)
            return state    # nothing to be done

    _refinement = ExpressionRefinement()  # static class member shared between instances
