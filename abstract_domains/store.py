from typing import List, Type, Dict, Callable

from abstract_domains.lattice import Lattice
from core.expressions import VariableIdentifier


class Store(Lattice):
    """Lifting Var -> L of a lattice L to a set of program variables Var."""

    def __init__(self, variables: List[VariableIdentifier],
                 lattices: Dict[Type, Callable[[VariableIdentifier], Lattice]]):
        """Create a mapping Var -> L from each variable in Var to the corresponding lattice element in L.

        :param variables: list of program variables
        :param lattices:
            dictionary mapping each variable type to the corresponding lattice type
            or a callable that generates a lattice
        """
        super().__init__()
        self._variables = variables
        self._lattices = lattices
        self._store = {var: self._lattices[var.typ](var) for var in self._variables}

    @property
    def variables(self):
        return self._variables

    @property
    def lattices(self):
        return self._lattices

    @property
    def store(self):
        return self._store

    def __repr__(self):
        return ", ".join("{}→{}".format(variable, value) for variable, value in self.store.items())

    def bottom(self) -> 'Store':
        for var in self.store:
            self.store[var].bottom()
        return self

    def top(self) -> 'Store':
        for var in self.store:
            self.store[var].top()
        return self

    def is_bottom(self) -> bool:
        """Test whether the store element is bottom, i.e. if *any* value in the store is bottom.

        :return: whether the store is bottom
        """
        return any(element.is_bottom() for element in self.store.values())

    def is_top(self) -> bool:
        return all(element.is_top() for element in self.store.values())

    def _less_equal(self, other: 'Store') -> bool:
        return all(self.store[var].less_equal(other.store[var]) for var in self.store)

    def _meet(self, other: 'Store'):
        for var in self.store:
            self.store[var].meet(other.store[var])
        return self

    def _join(self, other: 'Store') -> 'Store':
        for var in self.store:
            self.store[var].join(other.store[var])
        return self

    def _widening(self, other: 'Store'):
        return self._join(other)
