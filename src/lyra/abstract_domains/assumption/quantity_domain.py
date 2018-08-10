"""
Quantity Abstract Domain
========================

Non-relational abstract domain to be used for **input data assumptions analysis**.
The set of possible values of a program variables in a program state
is represented by their sign (negative, zero, positive, ...)

:Authors: Caterina Urban
"""
from collections import defaultdict
from typing import Set

from lyra.abstract_domains.assumption.assumption_domain import JSONMixin, InputMixin
from lyra.abstract_domains.numerical.sign_domain import SignLattice, SignState
from lyra.core.expressions import VariableIdentifier, Expression, Input, \
    BinaryArithmeticOperation, BinaryComparisonOperation, Literal
from lyra.core.types import BooleanLyraType, IntegerLyraType
from lyra.core.utils import copy_docstring


class QuantityLattice(SignLattice, JSONMixin):
    """Quantity lattice.

    .. image:: _static/sign.png

    .. document private methods
    .. automethod:: QuantityLattice._less_equal
    .. automethod:: QuantityLattice._meet
    .. automethod:: QuantityLattice._join
    .. automethod:: QuantityLattice._widening
    .. automethod:: QuantityLattice._neg
    .. automethod:: QuantityLattice._add
    .. automethod:: QuantityLattice._sub
    .. automethod:: QuantityLattice._mult
    """
    @copy_docstring(JSONMixin.to_json)
    def to_json(self) -> str:
        return str(self)

    @staticmethod
    @copy_docstring(JSONMixin.from_json)
    def from_json(json: str) -> 'JSONMixin':
        negative, zero, positive = False, False, False
        if json == '≤0' or json == '≠0' or json == '<0' or json == '⊤':
            negative = True
        if json == '≤0' or json == '=0' or json == '≥0' or json == '⊤':
            zero = True
        if json == '≥0' or json == '≠0' or json == '>0' or json == '⊤':
            positive = True
        return QuantityLattice(negative, zero, positive)


class QuantityState(SignState, InputMixin):
    """Quantity assumption analysis state. An element of the quantity assumption abstract domain.

    Map from each program variable to the sign representing its value.

    When reading input data, the corresponding quantity assumptions
    are stored in the class member ``inputs``, which is a map from each program point
    to the list of quantity assumptions on the input data read at that point.

    .. document private methods
    .. automethod:: QuantityState._assume
    .. automethod:: QuantityState._substitute
    """
    def __init__(self, variables: Set[VariableIdentifier], precursory: InputMixin = None):
        """Map each program variable to the interval representing its value.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: QuantityLattice)
        super(SignState, self).__init__(variables, lattices)
        InputMixin.__init__(self, precursory)

    @copy_docstring(InputMixin.replace)
    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'QuantityState':
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

    @copy_docstring(InputMixin.unify)
    def unify(self, other: 'QuantityState') -> 'QuantityState':
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

    class ExpressionRefinement(SignState.ExpressionRefinement):

        @copy_docstring(SignState.ExpressionRefinement.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            state.record(value)
            return state  # nothing to be done

        @copy_docstring(SignState.ExpressionRefinement.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            updated = super().visit_BinaryArithmeticOperation(expr, evaluation, value, state)
            if expr.operator == BinaryArithmeticOperation.Operator.Div:
                left = expr.right
                operator = BinaryComparisonOperation.Operator.NotEq
                right = Literal(IntegerLyraType(), "0")
                condition = BinaryComparisonOperation(BooleanLyraType(), left, operator, right)
                return updated.assume({condition})
            return updated

    _refinement = ExpressionRefinement()  # static class member shared between instances
