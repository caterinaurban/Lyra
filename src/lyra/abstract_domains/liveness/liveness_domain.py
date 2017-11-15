"""
Live Variable Abstract Domains
==============================

Abstract domains to be used for **live variable analysis**
and **strongly live variable analysis**.
A program variable is *live* in a state if
its value may be used before the variable is redefined.
A program variable is *strongly live* if
it is used in an assignment to another strongly live variable,
or if is used in a statement other than an assignment.

:Author: Caterina Urban
"""

from enum import IntEnum
from typing import List, Set

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.state import State
from lyra.core.expressions import Expression, VariableIdentifier

from lyra.abstract_domains.store import Store
from lyra.core.types import IntegerLyraType, BooleanLyraType
from lyra.core.utils import copy_docstring


class LivenessLattice(Lattice):
    """Liveness lattice::

        Live
          |
        Dead

    The default lattice element is ``Dead``.

    .. document private methods
    .. automethod:: LivenessLattice._less_equal
    .. automethod:: LivenessLattice._meet
    .. automethod:: LivenessLattice._join
    .. automethod:: LivenessLattice._widening
    """
    class Status(IntEnum):
        """Liveness status. The current lattice element is ether ``Live`` or ``Dead``."""
        Live = 1
        Dead = 0

    def __init__(self, liveness: Status = Status.Dead):
        super().__init__()
        self._element = liveness

    @property
    def element(self) -> Status:
        """Current lattice element."""
        return self._element

    def __repr__(self):
        return self.element.name

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'LivenessLattice':
        """The bottom lattice element is ``Dead``."""
        self.replace(LivenessLattice(LivenessLattice.Status.Dead))
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'LivenessLattice':
        """The top lattice element is ``Live``."""
        self.replace(LivenessLattice(LivenessLattice.Status.Live))
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return self.element == LivenessLattice.Status.Dead

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self.element == LivenessLattice.Status.Live

    @copy_docstring(Lattice.less_equal)
    def _less_equal(self, other: 'LivenessLattice') -> bool:
        return self.element < other.element

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'LivenessLattice') -> 'LivenessLattice':
        self.replace(LivenessLattice(min(self.element, other.element)))
        return self

    @copy_docstring(Lattice._join)
    def _join(self, other: 'LivenessLattice') -> 'LivenessLattice':
        self.replace(LivenessLattice(max(self.element, other.element)))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'LivenessLattice') -> 'LivenessLattice':
        return self._join(other)


class LivenessState(Store, State):
    """Live variable analysis state. An element of the live variable abstract domain.

    Map from each program variable to its liveness status.
    All program variables are *dead* by default.

    .. document private methods
    .. automethod:: LivenessState._assign_variable
    .. automethod:: LivenessState._assume
    .. automethod:: LivenessState._output
    .. automethod:: LivenessState._substitute_variable
    """
    def __init__(self, variables: List[VariableIdentifier]):
        """Map each program variable to its liveness status.

        :param variables: list of program variables
        """
        lattices = {BooleanLyraType: LivenessLattice, IntegerLyraType: LivenessLattice}
        super().__init__(variables, lattices)

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        """The current store is bottom if `all` of its variables map to a bottom element."""
        return all(element.is_bottom() for element in self.store.values())

    @copy_docstring(State._access_variable)
    def _access_variable(self, variable: VariableIdentifier) -> Set[Expression]:
        return {variable}

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: Expression, right: Expression):
        error = "A variable assignment is not expected in a backward analysis!"
        raise RuntimeError(error)

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'LivenessState':
        for identifier in condition.ids():
            if isinstance(identifier, VariableIdentifier):
                self.store[identifier] = LivenessLattice(LivenessLattice.Status.Live)
        return self

    @copy_docstring(State._evaluate_literal)
    def _evaluate_literal(self, literal: Expression) -> Set[Expression]:
        return {literal}

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'LivenessState':
        return self  # nothing to be donle

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: Expression, right: Expression) -> 'LivenessState':
        if isinstance(left, VariableIdentifier):
            self.store[left] = LivenessLattice(LivenessLattice.Status.Dead)
            for identifier in right.ids():
                if isinstance(identifier, VariableIdentifier):
                    self.store[identifier] = LivenessLattice(LivenessLattice.Status.Live)
                else:
                    error = f"Variable substitution with {right} is not implemented!"
                    raise NotImplementedError(error)
            return self
        error = f"Variable substitution for {left} is not implemented!"
        raise NotImplementedError(error)


class StrongLivenessState(LivenessState):
    """Strongly live variable analysis state. An element of the live variable abstract domain.

    Map from each program variable to its liveness status.
    All program variables are *dead* by default.

    .. document private methods
    .. automethod:: StrongLivenessState._assign_variable
    .. automethod:: StrongLivenessState._assume
    .. automethod:: StrongLivenessState._output
    .. automethod:: StrongLivenessState._substitute_variable
    """

    @copy_docstring(LivenessState._output)
    def _output(self, output: Expression) -> 'StrongLivenessState':
        for identifier in output.ids():
            if isinstance(identifier, VariableIdentifier):
                self.store[identifier] = LivenessLattice(LivenessLattice.Status.Live)
        return self

    @copy_docstring(LivenessState._substitute_variable)
    def _substitute_variable(self, left: Expression, right: Expression) -> 'StrongLivenessState':
        if isinstance(left, VariableIdentifier):
            if self.store[left].is_top():
                self.store[left] = LivenessLattice(LivenessLattice.Status.Dead)
                for identifier in right.ids():
                    if isinstance(identifier, VariableIdentifier):
                        live = LivenessLattice(LivenessLattice.Status.Live)
                        self.store[identifier] = live
                    else:
                        error = f"Variable substitution with {right} is not implemented!"
                        raise NotImplementedError(error)
            return self
        error = f"Variable substitution for {left} is not implemented!"
        raise NotImplementedError(error)
