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
from collections import defaultdict
from enum import IntEnum
from typing import Set

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.state import State
from lyra.core.expressions import Expression, VariableIdentifier, Subscription, Slicing

from lyra.abstract_domains.store import Store
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
        self._replace(LivenessLattice(LivenessLattice.Status.Dead))
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'LivenessLattice':
        """The top lattice element is ``Live``."""
        self._replace(LivenessLattice(LivenessLattice.Status.Live))
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return self.element == LivenessLattice.Status.Dead

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self.element == LivenessLattice.Status.Live

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'LivenessLattice') -> bool:
        return self.element <= other.element

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'LivenessLattice') -> 'LivenessLattice':
        self._replace(LivenessLattice(min(self.element, other.element)))
        return self

    @copy_docstring(Lattice._join)
    def _join(self, other: 'LivenessLattice') -> 'LivenessLattice':
        self._replace(LivenessLattice(max(self.element, other.element)))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'LivenessLattice') -> 'LivenessLattice':
        return self._join(other)


class LivenessState(Store, State):
    """Live variable analysis state.
    An element of the live variable abstract domain.

    Map from each program variable to its liveness status.
    All program variables are *dead* by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: LivenessState._assign
    .. automethod:: LivenessState._assume
    .. automethod:: LivenessState._output
    .. automethod:: LivenessState._substitute
    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        """Map each program variable to its liveness status.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: LivenessLattice)
        super().__init__(variables, lattices)
        State.__init__(self, precursory)

    @copy_docstring(Store.is_bottom)
    def is_bottom(self) -> bool:
        """The current store is bottom if `all` of its variables map to a bottom element."""
        return all(element.is_bottom() for element in self.store.values())

    def _assign_any(self, left: Expression, right: Expression):
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'LivenessState':
        return self._assign_any(left, right)

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'LivenessState':
        return self._assign_any(left, right)

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'LivenessState':
        return self._assign_any(left, right)

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression, bwd: bool = False) -> 'LivenessState':
        for identifier in condition.ids():
            self.store[identifier].top()
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute_any(self, left: Expression, right: Expression) -> 'LivenessState':
        if isinstance(left, VariableIdentifier):
            self.store[left].bottom()
            for identifier in right.ids():
                self.store[identifier].top()
            return self
        error = f"Substitution for {left} is not yet implemented!"
        raise NotImplementedError(error)

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'LivenessState':
        return self._substitute_any(left, right)

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'LivenessState':
        return self._substitute_any(left, right)

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'LivenessState':
        return self._substitute_any(left, right)


class StrongLivenessState(LivenessState):
    """Strongly live variable analysis state.
    An element of the strongly live variable abstract domain.

    Map from each program variable to its liveness status.
    All program variables are *dead* by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: StrongLivenessState._assign
    .. automethod:: StrongLivenessState._assume
    .. automethod:: StrongLivenessState._output
    .. automethod:: StrongLivenessState._substitute
    """

    @copy_docstring(LivenessState._output)
    def _output(self, output: Expression) -> 'StrongLivenessState':
        for identifier in output.ids():
            self.store[identifier] = LivenessLattice(LivenessLattice.Status.Live)
        return self

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'StrongLivenessState':
        if self.store[left].is_top():  # the assigned variable is strongly-live
            self.store[left].bottom()
            for identifier in right.ids():
                self.store[identifier].top()
        return self

    def _substitute_summary(self, left: Subscription, right: Expression) -> 'StrongLivenessState':
        """Substitute an expression to a summary variable.

        :param left: summary variable to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution
        """
        target = left.target
        if self.store[target].is_top():  # the target variable (list, dict,..) is strongly-live
            # summarization abstraction (weak update)
            for identifier in right.ids():
                self.store[identifier].top()
            if isinstance(left, Subscription):
                ids = left.key.ids()
            else:  # Slicing
                ids = left.lower.ids() | left.upper.ids()
            for identifier in ids:  # make ids in subscript strongly live
                self.store[identifier].top()
        return self

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'StrongLivenessState':
        return self._substitute_summary(left, right)

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'StrongLivenessState':
        return self._substitute_summary(left, right)
