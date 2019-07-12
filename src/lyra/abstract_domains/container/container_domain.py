
from collections import defaultdict
from typing import Set

from lyra.abstract_domains.basis import Basis
from lyra.abstract_domains.state import State
from lyra.abstract_domains.lattice import BottomMixin
from lyra.core.expressions import VariableIdentifier, Expression
from lyra.core.types import LyraType, DictLyraType


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


class ContainerState(Basis):

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        lattices = defaultdict(lambda: ContainerLattice)
        super().__init__(variables, lattices, precursory=precursory)

    def _assume(self, condition: Expression, bwd: bool = False) -> 'ContainerState':
        pass

    def _assign(self, left: Expression, right: Expression) -> 'ContainerState':
        if isinstance(left, VariableIdentifier):
            if isinstance(left.typ, DictLyraType):
                keys = set(right.keys)
                values = set(right.values)
            else:
                # for other (non-container) types, there are no keys
                keys = set()
                evaluation = self._evaluation.visit(right, self, dict())
                values = set(evaluation)
            self.store[left] = ContainerLattice(keys, values)
            return self
        else:
            return super()._assign(left, right)


