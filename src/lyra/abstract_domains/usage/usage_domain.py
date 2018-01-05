"""
Syntactic Usage Abstract Domain
===============================

Abstract domain to be used for **input data usage analysis** using syntactic variable dependencies.
A program variable can have value *U* (used), *S* (scoped), *W* (written), and *N* (not used).

:Authors: Simon Wehrli and Caterina Urban
"""

from enum import Flag
from typing import List
from copy import deepcopy

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, Slicing
from lyra.core.types import IntegerLyraType, BooleanLyraType, ListLyraType
from lyra.core.utils import copy_docstring


class UsageLattice(Lattice):
    """Usage lattice::

            U
          /   \\
        S       O
          \\   /
            N

    The default lattice element is ``N`` (not used).

    .. document private methods
    .. automethod:: UsageLattice._less_equal
    .. automethod:: UsageLattice._meet
    .. automethod:: UsageLattice._join
    .. automethod:: UsageLattice._widening
    """
    class Status(Flag):
        """Usage status.

        The current lattice element can be:

        * ``U`` (used): used at the current nesting level

        * ``S`` (scoped): used at a lower nesting level

        * ``W`` (written): used at a lower nesting level and modified at the current nesting level

        * ``N`` (not used): unused
        """
        U = 3
        S = 2
        W = 1
        N = 0

    def __init__(self, usage: Status = Status.N):
        super().__init__()
        self._element = usage

    @property
    def element(self):
        """Current lattice element."""
        return self._element

    def __repr__(self):
        return self.element.name

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        """The bottom lattice element is ``N`` (not used)."""
        self.replace(UsageLattice(UsageLattice.Status.N))
        return self

    def scoped(self):
        """Scoped lattice element.

        :return: current lattice element modified to be the scoped lattice element

        The scoped lattice element is ``S`` (scoped).
        """
        self.replace(UsageLattice(UsageLattice.Status.S))
        return self

    def written(self):
        """Written lattice element.

        :return: current lattice element modified to be the written lattice element

        The written lattice element is ``W`` (written).
        """
        self.replace(UsageLattice(UsageLattice.Status.W))
        return self

    @copy_docstring(Lattice.top)
    def top(self):
        """The top lattice element is ``U`` (used)."""
        self.replace(UsageLattice(UsageLattice.Status.U))
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self):
        return self.element == UsageLattice.Status.N

    def is_scoped(self):
        """Test whether the lattice element is ``S`` (scoped).

        :return: whether the lattice element is ``S`` (scoped)

        """
        return self.element == UsageLattice.Status.S

    def is_written(self):
        """Test whether the lattice element is ``W`` (written).

        :return: whether the lattice element is ``W`` (written)

        """
        return self.element == UsageLattice.Status.W

    @copy_docstring(Lattice.is_top)
    def is_top(self):
        return self.element == UsageLattice.Status.U

    def increase(self) -> 'UsageLattice':
        """Increase the nesting level.

        :return: current lattice element modified to reflect an increased nesting level
        """
        if self.is_top():
            return self.scoped()
        elif self.is_written():
            return self.bottom()
        return self

    def decrease(self, other: 'UsageLattice') -> 'UsageLattice':
        """Decrease the nesting level by combining lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to reflect a decreased nesting level
        """
        assert not self.is_written() or not other.is_scoped()
        if self.is_bottom() or other.is_written() or other.is_top():
            self.replace(other)
        return self

    @copy_docstring(Lattice.less_equal)
    def _less_equal(self, other: 'UsageLattice') -> bool:
        return self.element == other.element

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'UsageLattice') -> 'UsageLattice':
        self.replace(UsageLattice(self.element & other.element))
        return self

    @copy_docstring(Lattice._join)
    def _join(self, other: 'UsageLattice') -> 'UsageLattice':
        self.replace(UsageLattice(self.element | other.element))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'UsageLattice') -> 'UsageLattice':
        return self._join(other)


class UsageStore(Store):
    """An element of a store mapping each program variable to its usage status.

    All program variables are *not used* by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: UsageStore._less_equal
    .. automethod:: UsageStore._meet
    .. automethod:: UsageStore._join
    """
    def __init__(self, variables: List[VariableIdentifier]):
        """Map each program variable to its usage status.

        :param variables: list of program variables
        """
        types = [BooleanLyraType, IntegerLyraType, ListLyraType]
        lattices = {typ: UsageLattice for typ in types}
        super().__init__(variables, lattices)

    @copy_docstring(Store.is_bottom)
    def is_bottom(self) -> bool:
        """The current store is bottom if `all` of its variables map to a bottom element."""
        return all(element.is_bottom() for element in self.store.values())

    def increase(self) -> 'UsageStore':
        """Increase the nesting level.

        :return: current lattice element modified to reflect an increased nesting level

        The increase is performed point-wise for each variable.
        """
        for var in self.store:
            self.store[var].increase()
        return self

    def decrease(self, other: 'UsageStore') -> 'UsageStore':
        """Decrease the nesting level by combining lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to reflect a decreased nesting level

        The decrease is performed point-wise for each variable.
        """
        for var in self.store:
            self.store[var].decrease(other.store[var])
        return self


class UsageState(Stack, State):
    """Input data usage analysis state.
    An element of the syntactic usage abstract domain.

    Stack of maps from each program variable to its usage status.
    The stack contains a single map by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: UsageState._assign
    .. automethod:: UsageState._assume
    .. automethod:: UsageState._output
    .. automethod:: UsageState._substitute
    """
    def __init__(self, variables: List[VariableIdentifier]):
        super().__init__(UsageStore, {'variables': variables})

    @copy_docstring(Stack.push)
    def push(self):
        if self.is_bottom() or self.is_top():
            return self
        self.stack.append(deepcopy(self.lattice).increase())
        return self

    @copy_docstring(Stack.pop)
    def pop(self):
        if self.is_bottom() or self.is_top():
            return self
        current = self.stack.pop()
        self.lattice.decrease(current)
        return self

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'UsageState':
        effect = False      # effect of the current nesting level on the outcome of the program
        for variable in self.lattice.variables:
            value = self.lattice.store[variable]
            if value.is_written() or value.is_top():
                effect = True
        if effect:      # the current nesting level has an effect on the outcome of the program
            for identifier in condition.ids():
                if isinstance(identifier, VariableIdentifier):
                    self.lattice.store[identifier].top()
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'UsageState':
        return self.push()

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'UsageState':
        return self.pop()

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'UsageState':
        return self.push()

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'UsageState':
        return self.pop()

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'UsageState':
        for identifier in output.ids():
            if isinstance(identifier, VariableIdentifier):
                self.lattice.store[identifier].top()
        return self

    @copy_docstring(State.raise_error)
    def raise_error(self):
        return self

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'UsageState':
        if isinstance(left, VariableIdentifier):
            if self.lattice.store[left].is_top() or self.lattice.store[left].is_scoped():
                # the assigned variable is used or scoped
                self.lattice.store[left].written()
                for identifier in right.ids():
                    if isinstance(identifier, VariableIdentifier):
                        self.lattice.store[identifier].top()
                    else:
                        error = f"Substitution with {right} is not implemented!"
                        raise NotImplementedError(error)
            return self
        elif isinstance(left, Subscription) or isinstance(left, Slicing):
            target = left.target
            if self.lattice.store[target].is_top() or self.lattice.store[target].is_scoped():
                # the assigned variable is used or scoped
                self.lattice.store[target].top()      # summarization abstraction
                for identifier in right.ids():
                    if isinstance(identifier, VariableIdentifier):
                        self.lattice.store[identifier].top()
                    else:
                        error = f"Substitution with {right} is not implemented!"
                        raise NotImplementedError(error)
            return self
        error = f"Substitution for {left} is not yet implemented!"
        raise NotImplementedError(error)
