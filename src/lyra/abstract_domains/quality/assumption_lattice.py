"""
Assumption Lattice
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from enum import IntEnum, Enum

from lyra.abstract_domains.lattice import Lattice, BottomMixin, TopMixin
from lyra.abstract_domains.numerical.interval_domain import IntervalLattice
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

    def is_real(self) -> 'bool':
        """
        Returns True if the current type lattice element is of type float
        """
        return self.element == TypeLattice.Status.Float

    def is_integer(self) -> 'bool':
        """
        Returns True if the current type lattice element is of type int
        """
        return self.element == TypeLattice.Status.Int

    def is_boolean(self) -> 'bool':
        """
        Returns True if the current type lattice element is of type bool
        """
        return self.element == TypeLattice.Status.Bool

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
    The Assumption Lattice is represented as a dictionary with different kinds of assumptions.
    The 'type_assmp' element is an assumption of the type.
    The 'range_assmp' element is an assumption about the range.

    The default element is the tuple with all assumption elements set to top.

    .. document private methods
    .. automethod:: AssumptionLattice._less_equal
    .. automethod:: AssumptionLattice._meet
    .. automethod:: AssumptionLattice._join
    .. automethod:: AssumptionLattice._widening
    """

    class Assumption(Enum):
        """
        Name of the assumptions that are covered by the assumption lattice

        * ``type_assmp``: Used for assumptions about the type

        * ``range_assmp``: Used for assumptions about the range of values
        """

        type_assmp = 'type_assmp'
        range_assmp = 'range_assmp'

    def __init__(self, type_element=None, range_element=None):
        super().__init__()
        if type_element is None:
            type_element = TypeLattice().top()
        if range_element is None:
            range_element = IntervalLattice().top()
        self._assumptions = {
            AssumptionLattice.Assumption.type_assmp: type_element,
            AssumptionLattice.Assumption.range_assmp: range_element
        }

    def __repr__(self):
        assumptions = [self.type_assumption, self.range_assumption]
        assumption_repr = [assumption.__repr__() for assumption in assumptions]
        comma_separated = ', '.join(assumption_repr)
        return f'({comma_separated})'

    @property
    def assumptions(self):
        return self._assumptions

    @property
    def type_assumption(self):
        return self.assumptions[AssumptionLattice.Assumption.type_assmp]

    @property
    def range_assumption(self):
        return self.assumptions[AssumptionLattice.Assumption.range_assmp]

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        for assumption in self.assumptions.values():
            assumption.bottom()
        return self

    @copy_docstring(Lattice.top)
    def top(self):
        for assumption in self.assumptions.values():
            assumption.top()
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        for assumption in self.assumptions.values():
            if assumption.is_bottom():
                return True
        return False

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        for assumption in self.assumptions.values():
            if not assumption.is_top():
                return False
        return True

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'AssumptionLattice') -> bool:
        return self.type_assumption.less_equal(other.type_assumption) \
               and self.range_assumption.less_equal(other.range_assumption)

    @copy_docstring(Lattice._join)
    def _join(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.join(other.type_assumption)
        self.range_assumption.join(other.range_assumption)
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.meet(other.type_assumption)
        self.range_assumption.meet(other.range_assumption)
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.widening(other.type_assumption)
        self.range_assumption.widening(other.range_assumption)
        return self


class InputAssumptionLattice(BottomMixin, TopMixin):
    """
    The Assumption Lattice is represented as a list containing the assumptions made about the
    input in the correct order

    The default element is an empty list.

    .. document private methods
    .. automethod:: AssumptionLattice._less_equal
    .. automethod:: AssumptionLattice._meet
    .. automethod:: AssumptionLattice._join
    .. automethod:: AssumptionLattice._widening
    """

    def __init__(self):
        super().__init__()
        self._input_assmp_backwards = []

    def __repr__(self):
        if self.is_bottom():
            return '⊥'
        if self.is_top():
            return 'T'
        assumption_repr = [assumption.__repr__() for assumption in self._input_assmp_backwards]
        comma_separated = ', '.join(assumption_repr)
        return f'[{comma_separated}]'

    @property
    def assumptions(self):
        if self.is_bottom() or self.is_top():
            return []
        return self._input_assmp_backwards

    def add_assumption(self, assumption: AssumptionLattice):
        """
        Adds the assumption to the input assumption list
        """
        self._input_assmp_backwards.append(assumption)

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'InputAssumptionLattice') -> bool:
        if len(self._input_assmp_backwards) == len(other._input_assmp_backwards):
            for assmp1, assmp2 in zip(self._input_assmp_backwards, other._input_assmp_backwards):
                if not assmp1.less_equal(assmp2):
                    return False
            return True
        return False

    @copy_docstring(Lattice._join)
    def _join(self, other: 'InputAssumptionLattice') -> 'InputAssumptionLattice':
        if len(self._input_assmp_backwards) != len(other._input_assmp_backwards):
            self.top()
        else:
            for assmp1, assmp2 in zip(self._input_assmp_backwards, other._input_assmp_backwards):
                assmp1.join(assmp2)
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'InputAssumptionLattice') -> 'InputAssumptionLattice':
        if len(self._input_assmp_backwards) != len(other._input_assmp_backwards):
            self._input_assmp_backwards = []
        else:
            for assmp1, assmp2 in zip(self._input_assmp_backwards, other._input_assmp_backwards):
                assmp1.meet(assmp2)
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'InputAssumptionLattice') -> 'InputAssumptionLattice':
        if len(self._input_assmp_backwards) != len(other._input_assmp_backwards):
            self._input_assmp_backwards = []
        else:
            for assmp1, assmp2 in zip(self._input_assmp_backwards, other._input_assmp_backwards):
                assmp1.widening(assmp2)
        return self

