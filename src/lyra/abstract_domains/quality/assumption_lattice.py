"""
Assumption Lattice
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from enum import IntEnum

from lyra.abstract_domains.lattice import Lattice, BottomMixin
from lyra.core.types import LyraType, BooleanLyraType, IntegerLyraType, FloatLyraType
from lyra.core.utils import copy_docstring


class TypeLattice(BottomMixin):
    """Type Lattice::

        Any
         |
        Float
         |
        Int
         |
        Bool

    The default lattice element is ``Any``.

    .. document private methods
    .. automethod:: TypeLattice._less_equal
    .. automethod:: TypeLattice._meet
    .. automethod:: TypeLattice._join
    .. automethod:: TypeLattice._widening
    """

    class Status(IntEnum):
        """Type status.

        The current lattice element can be:

        * ``Any``: Used as top element for any type

        * ``Float``: Float type

        * ``Int`` Integer type

        * ``Bool`` Boolean type
        """
        Any = 3
        Float = 2
        Int = 1
        Bool = 0

    def __init__(self, type_status: Status = Status.Any):
        super().__init__()
        self._element = type_status

    @classmethod
    def from_lyra_type(cls, lyra_type: LyraType):
        if isinstance(lyra_type, BooleanLyraType):
            return cls(TypeLattice.Status.Bool)
        elif isinstance(lyra_type, IntegerLyraType):
            return cls(TypeLattice.Status.Int)
        elif isinstance(lyra_type, FloatLyraType):
            return cls(TypeLattice.Status.Float)
        return cls(TypeLattice.Status.Any)

    @property
    def element(self) -> Status:
        if self.is_bottom():
            return None
        return self._element

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return self.element.name

    @copy_docstring(Lattice.top)
    def top(self) -> 'TypeLattice':
        self.replace(TypeLattice(TypeLattice.Status.Any))
        return self

    def real(self) -> 'TypeLattice':
        """Float lattice element.

        :return: current lattice element modified to be the Float lattice element
        """
        self.replace(TypeLattice(TypeLattice.Status.Float))
        return self

    def integer(self) -> 'TypeLattice':
        """Int lattice element.

        :return: current lattice element modified to be the Int lattice element
        """
        self.replace(TypeLattice(TypeLattice.Status.Int))
        return self

    def boolean(self) -> 'TypeLattice':
        """Bool lattice element.

        :return: current lattice element modified to be the Bool lattice element
        """
        self.replace(TypeLattice(TypeLattice.Status.Bool))
        return self

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self.element == TypeLattice.Status.Any

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'TypeLattice') -> bool:
        return self.element <= other.element

    @copy_docstring(Lattice._join)
    def _join(self, other: 'TypeLattice') -> 'TypeLattice':
        self.replace(TypeLattice(max(self.element, other.element)))
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'TypeLattice') -> 'TypeLattice':
        self.replace(TypeLattice(min(self.element, other.element)))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'TypeLattice') -> 'TypeLattice':
        return self._join(other)


class AssumptionLattice(Lattice):
    """

    .. document private methods
    .. automethod:: AssumptionLattice._less_equal
    .. automethod:: AssumptionLattice._meet
    .. automethod:: AssumptionLattice._join
    .. automethod:: AssumptionLattice._widening
    """

    def __repr__(self):
        pass

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'AssumptionLattice':
        pass

    @copy_docstring(Lattice.top)
    def top(self) -> 'AssumptionLattice':
        pass

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        pass

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        pass

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'AssumptionLattice') -> bool:
        pass

    @copy_docstring(Lattice._join)
    def _join(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        pass

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        pass

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        pass

