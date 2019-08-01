
from collections import defaultdict
from typing import Set

from lyra.abstract_domains.assumption.assumption_domain import InputMixin
from lyra.abstract_domains.basis import Basis
from lyra.abstract_domains.state import State
from lyra.abstract_domains.lattice import BottomMixin
from lyra.abstract_domains.numerical.interval_domain import Input

from lyra.core.expressions import VariableIdentifier, Expression, Subscription, SetDisplay, ListDisplay, \
    BinaryComparisonOperation, Keys, DictDisplay
from lyra.core.types import LyraType
from lyra.core.utils import copy_docstring



class ContainerLattice(BottomMixin):
    """Container lattice.

    The default abstraction is ``(∅, ∅)`` (empty set of keys, empty set of values), representing that
    no keys and no values must be in the container.

    The bottom element of the lattice is ``⊥``,  which represents that all the possible keys and all the
    possible values must be in the container.

    .. document private methods
    .. automethod:: ContainerLattice._less_equal
    .. automethod:: ContainerLattice._meet
    .. automethod:: ContainerLattice._join
    .. automethod:: ContainerLattice._widening
    """

    def __init__(self, keys: Set[LyraType] = None, values: Set[LyraType] = None):
        super().__init__()
        if keys is not None and values is not None:
            self._keys = keys
            self._values = values
        else:
            self.top()

    @property
    def keys(self):
        """Current set of keys that must be in the container.

        :return: the current set of keys
        """
        return self._keys

    @property
    def values(self):
        """Current set of values that must be in the container.

        :return: the current set of values
        """
        return self._values

    def __repr__(self):
        if self.is_bottom():
            return "⊥";
        if not self.keys:
            keys = "∅"
        else:
            keys = ", ".join("{}".format(key) for key in self.keys)
            keys = "{" + keys + "}"
        if not self.values:
            values = "∅"
        else:
            values = ", ".join("{}".format(value) for value in self.values)
            values = "{" + values + "}"
        return "(" + keys + ", " + values + ")"

    def top(self):
        """The top lattice element is the pair ``(∅, ∅)``."""
        return self._replace(type(self)(set(), set()))

    def is_top(self) -> bool:
        return not self.keys and not self.values

    def _less_equal(self, other: 'ContainerLattice') -> bool:
        return other.keys.issubset(self.keys) and other.values.issubset(self.values)

    def _join(self, other: 'ContainerLattice') -> 'ContainerLattice':
        keys = self.keys.intersection(other.keys)
        values = self.values.intersection(other.values)
        return self._replace(type(self)(keys, values))

    def _meet(self, other: 'ContainerLattice') -> 'ContainerLattice':
        keys = self.keys.union(other.keys)
        values = self.values.union(other.values)
        return self._replace(type(self)(keys, values))

    def _widening(self, other: 'ContainerLattice') -> 'ContainerLattice':
        return self.join(other)


class ContainerState(Basis, InputMixin):

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        lattices = defaultdict(lambda: ContainerLattice)
        super().__init__(variables, lattices, precursory=precursory)
        InputMixin.__init__(self, precursory)

    def _assume(self, condition: Expression, bwd: bool = False) -> 'ContainerState':
        return self

    def _substitute(self, left: Expression, right: Expression) -> 'ContainerState':
        if isinstance(right, Subscription):
            target = right.target
            key = right.key
            current_state = self.store[target]
            keys = set(self._evaluation.visit(key, self, dict()))
            self.store[target] = ContainerLattice(current_state.keys.union(keys), current_state.values)
            return self
        if isinstance(right, (SetDisplay, ListDisplay, DictDisplay)):
            # constant, so the dictionary/list becomes top
            keys = set()
            values = set()
            self.store[left] = ContainerLattice(keys, values)
            return self
        if isinstance(left, Subscription):
            # nothing changes, as we don't know if the key was there before or not
            return self
        else:
            return super()._substitute(left, right)

    @copy_docstring(InputMixin.replace)
    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'ContainerState':
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
    def unify(self, other: 'ContainerState') -> 'ContainerState':
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

    class ExpressionRefinement(Basis.ExpressionRefinement):

        @copy_docstring(Basis.ExpressionRefinement.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            state.record(value)
            return state  # nothing to be done

        @copy_docstring(Basis.ExpressionRefinement.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            if isinstance(expr.right, Subscription):
                target = expr.right.target
                key = expr.right.key
                current_state = state.store[target]
                keys = {key}
                state.store[target] = ContainerLattice(current_state.keys.union(keys), current_state.values)
            return state

    _refinement = ExpressionRefinement()  # static class member shared between instances

