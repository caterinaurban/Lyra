"""
Assumption Lattice
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from enum import IntEnum, Enum

from copy import deepcopy

from lyra.abstract_domains.lattice import Lattice, BottomMixin, BoundedLattice
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


class InputAssumptionLattice(BoundedLattice):
    """
    The Input Assumption Lattice consists of two elements:
    iterations: the number of times the same assumption applies
    assumptions: the assumption for those inputs

    The default element is 1 iteration number and an empty list.

    .. document private methods
    .. automethod:: AssumptionLattice._less_equal
    .. automethod:: AssumptionLattice._meet
    .. automethod:: AssumptionLattice._join
    .. automethod:: AssumptionLattice._widening
    """

    def __init__(self, iterations=1, assmps=None):
        super().__init__()
        self.iterations = iterations
        if assmps is None:
            self._assmps = []
        else:
            self._assmps = assmps
        self.is_loop = False
        self.condition = None

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        if self.is_top():
            return "T"
        if self.iterations is None:
            return "NONE"
        if self.iterations == 1:
            return self.assmps.__repr__()
        return f"{self.iterations} x {self.assmps.__repr__()}"

    @property
    def assmps(self):
        if self.is_bottom() or self.is_top():
            return None
        return self._assmps

    def add_assumption_front(self, assmp: AssumptionLattice):
        """Adds an assumption to the front of the assumption list.

        :param assmp: assumption to be added to the list of current assumptions
        """
        assert isinstance(assmp, AssumptionLattice)
        self._assmps.insert(0, assmp)

    def add_assumptions_front(self, assmps: [AssumptionLattice]):
        """Adds multiple assumption to the front of the assumption list.

        :param assmps: list of assumptions to be added to the list of current assumptions
        """
        self._assmps = assmps + self.assmps

    def add_assumptions_with_iter(self, iterations: int, assmps, is_loop=True):
        """Adds assumptions to the front of the assumption list and sets the itartion number.

        :param iterations: number of times the assumptions appear in input file
        :param assmps: list of assumptions to be added to the list of current assumptions
        """
        input_assmps = InputAssumptionLattice(iterations, assmps)
        input_assmps.is_loop = is_loop
        self._assmps.insert(0, input_assmps)

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'InputAssumptionLattice') -> bool:
        if len(self.assmps) != len(other.assmps):
            return False
        for assmp1, assmp2 in zip(self.assmps, other.assmps):
            if not assmp1.less_equal(assmp2):
                return False
        return True

    @copy_docstring(Lattice._join)
    def _join(self, other: 'InputAssumptionLattice') -> 'InputAssumptionLattice':
        if len(self.assmps) == len(other.assmps) == 0:
            return self
        if len(self.assmps) == 0 or len(other.assmps) == 0:
            return self.top()
        self_is_case = isinstance(self.assmps[0], InputAssumptionLattice)
        self_is_case = self_is_case and not self.assmps[0].is_loop
        other_is_case = isinstance(other.assmps[0], InputAssumptionLattice)
        other_is_case = other_is_case and not other.assmps[0].is_loop
        if self_is_case and other_is_case:
            self.join_case(other)
            return self
        elif not self_is_case and not other_is_case:
            self.join_loop(other)
            return self
        elif self_is_case and isinstance(other.assmps[0], AssumptionLattice):
            if len(self.assmps[0].assmps) == 1 and self.assmps[0].assmps[0] == other.assmps[0]:
                self._assmps = deepcopy(other.assmps)
                return self
        elif other_is_case and isinstance(self.assmps[0], AssumptionLattice):
            if len(other.assmps[0].assmps) == 1 and other.assmps[0].assmps[0] == self.assmps[0]:
                return self
        self.assmps.clear()
        return self

    def join_case(self, other):
        new_assmps = []
        iter_self = 0
        iter_other = 0
        while iter_self < len(self.assmps[0].assmps) or iter_other < len(other.assmps[0].assmps):
            if iter_self < len(self.assmps[0].assmps):
                curr_self = self.assmps[0].assmps[iter_self]
            else:
                curr_self = None
            if iter_other < len(other.assmps[0].assmps):
                curr_other = other.assmps[0].assmps[iter_other]
            else:
                curr_other = None
            self_is_None = isinstance(curr_self, InputAssumptionLattice) and curr_self.iterations is None
            other_is_None = isinstance(curr_other, InputAssumptionLattice) and curr_other.iterations is None
            if self_is_None and other_is_None:
                new_assmps.append(curr_self)
                iter_self += 1
                iter_other += 1
                continue
            if curr_self is None or curr_other is None:
                break
            if self_is_None and not isinstance(curr_other, InputAssumptionLattice):
                return self.top()
            if other_is_None and not isinstance(curr_self, InputAssumptionLattice):
                return self.top()
            if self_is_None and curr_other.is_loop:
                new_assmps.append(curr_other)
                iter_self += 1
                iter_other += 1
                continue
            if other_is_None and curr_self.is_loop:
                new_assmps.append(curr_self)
                iter_self += 1
                iter_other += 1
                continue
            if curr_self is None or curr_other is None:
                break
            if type(curr_other) != type(curr_self):
                break
            new_assmps.append(curr_self.join(curr_other))
            iter_self += 1
            iter_other += 1
        self.assmps[0]._assmps = new_assmps
        return self

    def join_loop(self, other):
        if len(self.assmps) == len(other.assmps):
            new_assmps = []
            for assmp1, assmp2 in zip(self.assmps, other.assmps):
                assmp1_inputlattice = isinstance(assmp1, InputAssumptionLattice)
                assmp2_inputlattice = isinstance(assmp2, InputAssumptionLattice)
                if assmp1_inputlattice and assmp1.iterations is None:
                    new_assmps.append(assmp2)
                elif assmp2_inputlattice and assmp2.iterations is None:
                    new_assmps.append(assmp1)
                elif assmp1_inputlattice == assmp2_inputlattice:
                    new_assmps.append(assmp1.join(assmp2))
                else:
                    self.assmps.clear()
                    return self
            self._assmps = new_assmps
            return self

        if len(self.assmps) > len(other.assmps):
            if isinstance(other.assmps[0], InputAssumptionLattice):
                other_is_placeholder = other.assmps[0].iterations is None
                self_are_inputlattices = isinstance(self.assmps[0], InputAssumptionLattice)
                self_are_inputlattices &= isinstance(self.assmps[1], InputAssumptionLattice)
                if other_is_placeholder and self_are_inputlattices:
                    self.assmps[0].join(self.assmps[1])
                    self.assmps.pop(1)
                    assert len(self.assmps) == len(other.assmps)
                    self.join(other)
                    return self
        elif len(other.assmps) > len(self.assmps):
            if isinstance(self.assmps[0], InputAssumptionLattice):
                self_is_placeholder = self.assmps[0].iterations is None
                other_are_inputlattices = isinstance(other.assmps[0], InputAssumptionLattice)
                other_are_inputlattices &= isinstance(other.assmps[1], InputAssumptionLattice)
                if self_is_placeholder and other_are_inputlattices:
                    other_copy = deepcopy(other)
                    other_copy.assmps[0].join(other_copy.assmps[1])
                    other_copy.assmps.pop(1)
                    assert len(self.assmps) == len(other_copy.assmps)
                    self.join(other_copy)
                    return self
        self.assmps.clear()
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'InputAssumptionLattice'):
        raise NotImplementedError(f"Meet for {self} and {other} is not implemented.")

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'InputAssumptionLattice'):
        raise NotImplementedError(f"Widening for {self} and {other} is not implemented.")




