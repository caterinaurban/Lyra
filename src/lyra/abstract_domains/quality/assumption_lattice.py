"""
Assumption Lattice
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from enum import IntEnum, Enum

from copy import deepcopy

from lyra.abstract_domains.lattice import Lattice, BottomMixin, BoundedLattice
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
    def element(self):
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
        """

        type_assmp = 'type_assmp'

    def __init__(self, type_element=None):
        super().__init__()
        if type_element is None:
            type_element = TypeLattice().top()
        self._assumptions = {
            AssumptionLattice.Assumption.type_assmp: type_element
        }
        self.pp = None

    def __repr__(self):
        assumptions = [self.type_assumption]
        assumption_repr = [assumption.__repr__() for assumption in assumptions]
        comma_separated = ', '.join(assumption_repr)
        return f'({comma_separated})'

    @property
    def assumptions(self):
        return self._assumptions

    @property
    def type_assumption(self):
        return self.assumptions[AssumptionLattice.Assumption.type_assmp]

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
        return self.type_assumption.less_equal(other.type_assumption)

    @copy_docstring(Lattice._join)
    def _join(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.join(other.type_assumption)
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.meet(other.type_assumption)
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'AssumptionLattice') -> 'AssumptionLattice':
        self.type_assumption.widening(other.type_assumption)
        return self


class InputAssumptionLattice(BoundedLattice):
    """
    The Input Assumption Lattice consists of four elements:
    var_name: the name of the variable that was substituted for the input
    assmp: an element of the AssumptionLattice with the assumption for the input
    relations: relational assumption of the input
    input_info: information about locations of related inputs

    The default element is (None, Any, None, {})

    .. document private methods
    .. automethod:: InputAssumptionLattice._less_equal
    .. automethod:: InputAssumptionLattice._meet
    .. automethod:: InputAssumptionLattice._join
    .. automethod:: InputAssumptionLattice._widening
    """

    def __init__(self, var_name=None, assmp=None, relations=None, input_info=None):
        super().__init__()
        self.var_name = var_name
        self.relations = relations
        self.input_info = input_info if input_info is not None else {}
        self.assmp = assmp if assmp is not None else AssumptionLattice()
        self.infoloss = False

    @property
    def input_id(self):
        return self.input_info[self.var_name]

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        if self.is_top():
            return "T"
        input_info = {k.__str__(): v for k, v in self.input_info.items()}
        return f'({self.var_name}, {self.assmp.__repr__()}, {self.relations}, {input_info})'

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'InputAssumptionLattice') -> bool:
        if self.infoloss and other.infoloss:
            return True
        if self.infoloss or other.infoloss:
            return False
        if (self.var_name is None) != (other.var_name is None):
            return False
        if not self.assmp.less_equal(other.assmp):
            return False
        if not self.relations.less_equal(other.relations):
            return False
        if self.input_info != other.input_info:
            return False
        return True

    @copy_docstring(Lattice._join)
    def _join(self, other: 'InputAssumptionLattice') -> 'InputAssumptionLattice':
        if self.infoloss:
            return self
        if other.infoloss:
            return self.replace(deepcopy(other))
        self.assmp.join(other.assmp)
        if self.var_name != other.var_name:
            self.infoloss = True
            return self
        else:
            self.relations.join(other.relations)
        if self.input_info != other.input_info:
            for var_name, input_index in self.input_info.items():
                if input_index > other.input_info[var_name]:
                    self.input_info[var_name] = other.input_info[var_name]
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'InputAssumptionLattice'):
        raise NotImplementedError(f"Meet for {self} and {other} is not implemented.")

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'InputAssumptionLattice'):
        raise NotImplementedError(f"Widening for {self} and {other} is not implemented.")


class MultiInputAssumptionLattice(BoundedLattice):
    """
    The Input Assumption Lattice consists of two elements:
    iterations: for how many values the assumption holds
    assmps: the assumptions that hold

    The default element is (1, [])

    .. document private methods
    .. automethod:: MultiInputAssumptionLattice._less_equal
    .. automethod:: MultiInputAssumptionLattice._meet
    .. automethod:: MultiInputAssumptionLattice._join
    .. automethod:: MultiInputAssumptionLattice._widening
    """

    def __init__(self, iterations=1, assmps=None, pp=None):
        super().__init__()
        self.iterations = iterations
        self._assmps = assmps if assmps is not None else []
        self.pp = pp
        self.infoloss = False
        self.is_main = False
        self.is_loop = False
        self.join_as_loop = False
        self.condition = None
        self.input_id = None

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        if self.is_top():
            return "T"
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
        self._assmps.insert(0, assmp)

    def add_assumptions_front(self, assmps: [AssumptionLattice]):
        """Adds multiple assumption to the front of the assumption list.

        :param assmps: list of assumptions to be added to the list of current assumptions
        """
        self._assmps = assmps + self.assmps

    def add_assmps_with_iter(self, iterations: int, assmps, pp):
        """Adds assumptions to the front of the assumption list and sets the iteration number.

        :param iterations: number of times the assumptions appear in the input file
        :param assmps: list of assumptions to be added to the list of current assumptions
        :param pp: program point of the first assumption
        """
        input_assmps = MultiInputAssumptionLattice(iterations, assmps, pp)
        input_assmps.is_loop = True
        input_assmps.input_id = pp.line
        self._assmps.insert(0, input_assmps)

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'MultiInputAssumptionLattice') -> bool:
        if self.infoloss and other.infoloss:
            return True
        if self.infoloss or other.infoloss:
            return False
        if self.iterations != other.iterations:
            return False
        if isinstance(self.assmps, list) and isinstance(other.assmps, list):
            if len(self.assmps) == len(other.assmps):
                for assmp1, assmp2 in zip(self.assmps, other.assmps):
                    if type(assmp1) != type(assmp2):
                        return False
                    if not assmp1.less_equal(assmp2):
                        return False
                return True
            return False
        return False

    @copy_docstring(Lattice._join)
    def _join(self, other: 'MultiInputAssumptionLattice') -> 'MultiInputAssumptionLattice':
        if self.infoloss:
            return self
        if other.infoloss:
            return self.replace(deepcopy(other))
        if len(self.assmps) == len(other.assmps) == 0:
            return self
        if self.join_as_loop:
            assert other.join_as_loop
            if len(self.assmps) == 0:
                self.replace(deepcopy(other))
                return self
            elif len(other.assmps) == 0:
                return self
            self_input_pp = self.assmps[0].input_id
            other_input_pp = other.assmps[0].input_id
            if self_input_pp == other_input_pp:
                return self
            elif self_input_pp < other_input_pp:
                self._assmps = self.assmps[:1] + other.assmps
                return self
            else:
                self._assmps = deepcopy(other.assmps[:1]) + self.assmps
                return self
        if len(self.assmps) != len(other.assmps) and not self.is_main:
            self.assmps.clear()
            self.infoloss = True
            return self
        if self.is_main:
            self.join_cases(other)
        else:
            new_assmps = []
            for assmp1, assmp2 in zip(self.assmps, other.assmps):
                if type(assmp1) != type(assmp2) or assmp1.infoloss or assmp2.infoloss:
                    self.assmps.clear()
                    if not self.is_main:
                        self.infoloss = True
                    return self
                else:
                    new_assmps.append(deepcopy(assmp1).join(assmp2))
                    if assmp1.infoloss:
                        self.assmps.clear()
                        if not self.is_main:
                            self.infoloss = True
                        return self

            self._assmps = new_assmps
        return self

    def join_cases(self, other: 'MultiInputAssumptionLattice'):
        """Joins two MultiInputAssumptionLattice. It unrolls assumptions in loops if necessary.

        [a] ⊔ [b] = [a ⊔ b]

        [N x [a]] ⊔ [b1, b2] = [a ⊔ b1, [(N-1) x [a]] ⊔ [b2]]

        [N x [a1], a2] ⊔ [M x [b1], b2] with N < M:  [N x [a1 ⊔ b1], [a2] ⊔ [(M-N) x [b1], b2]]

        :param other: other InputAssumptionLattice that should be joined with self
        """
        self_stack = self.assmps
        other_stack = other.assmps
        final_assmps = []
        while len(self_stack) > 0 and len(other_stack) > 0:
            curr_self = self_stack.pop(0)
            curr_other = other_stack.pop(0)
            self_assmp_lattice = isinstance(curr_self, InputAssumptionLattice)
            other_assmp_lattice = isinstance(curr_other, InputAssumptionLattice)
            if self_assmp_lattice and other_assmp_lattice:
                curr_self.join(curr_other)
                if curr_self.infoloss:
                    break
                final_assmps.append(curr_self)
            elif not self_assmp_lattice and not other_assmp_lattice:
                assert isinstance(curr_self, MultiInputAssumptionLattice)
                assert isinstance(curr_other, MultiInputAssumptionLattice)
                if curr_self.iterations == curr_other.iterations:
                    for assmp1, assmp2 in zip(curr_self.assmps, curr_other.assmps):
                        assmp1.join(assmp2)
                        if assmp1.infoloss:
                            break
                    final_assmps.append(curr_self)
                elif curr_self.iterations < curr_other.iterations:
                    copy_other_first = deepcopy(curr_other)
                    copy_other_first.iterations = curr_self.iterations
                    copy_other_second = deepcopy(curr_other)
                    copy_other_second.iterations -= curr_self.iterations
                    if copy_other_second.iterations == 1:
                        other_stack = copy_other_second.assmps + other_stack
                    else:
                        other_stack.insert(0, copy_other_second)
                    other_stack.insert(0, copy_other_first)
                    self_stack.insert(0, curr_self)
                else:
                    copy_self = deepcopy(curr_self)
                    copy_self.iterations = curr_other.iterations
                    curr_self.iterations -= curr_other.iterations
                    if curr_self.iterations == 1:
                        self_stack = curr_self.assmps + self_stack
                    else:
                        self_stack.insert(0, curr_self)
                    self_stack.insert(0, copy_self)
                    other_stack.insert(0, curr_other)
            elif self_assmp_lattice:
                assert isinstance(curr_other, MultiInputAssumptionLattice)
                copy_other = deepcopy(curr_other)
                copy_other.iterations -= 1
                if copy_other.iterations == 1:
                    other_stack = copy_other.assmps + other_stack
                else:
                    other_stack.insert(0, copy_other)
                other_stack = curr_other.assmps + other_stack
                self_stack.insert(0, curr_self)
            else:
                assert isinstance(curr_self, MultiInputAssumptionLattice)
                assert isinstance(curr_other, InputAssumptionLattice)
                copy_self = deepcopy(curr_self)
                copy_self.iterations -= 1
                if copy_self.iterations == 1:
                    self_stack = copy_self.assmps + self_stack
                else:
                    self_stack.insert(0, copy_self)
                self_stack = curr_self.assmps + self_stack
                other_stack.insert(0, curr_other)
        self._assmps = final_assmps

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'MultiInputAssumptionLattice'):
        raise NotImplementedError(f"Meet for {self} and {other} is not implemented.")

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'MultiInputAssumptionLattice'):
        raise NotImplementedError(f"Widening for {self} and {other} is not implemented.")
