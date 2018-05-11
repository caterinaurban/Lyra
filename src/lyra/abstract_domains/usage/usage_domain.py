"""
Syntactic Usage Abstract Domain
===============================

Abstract domain to be used for **input data usage analysis** using syntactic variable dependencies.
A program variable can have value *U* (used), *S* (scoped), *W* (written), and *N* (not used).

:Authors: Caterina Urban and Simon Wehrli
"""

from copy import deepcopy
from typing import List, Dict, Type

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.abstract_domains.usage.usage_lattice import UsageLattice
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, Slicing
from lyra.core.types import IntegerLyraType, BooleanLyraType, ListLyraType, NdarrayLyraType
from lyra.core.utils import copy_docstring


class UsageStore(Store):
    """An element of a store mapping each program variable to its usage status.

    All program variables are *not used* by default.

    .. document private methods
    .. automethod:: UsageStore._less_equal
    .. automethod:: UsageStore._meet
    .. automethod:: UsageStore._join
    """
    def __init__(self, variables: List[VariableIdentifier], lattices: Dict[Type, Type[Lattice]]):
        """Map each program variable to its usage status.

        :param variables: list of program variables
        :param lattices: dictionary from variable types to the corresponding lattice types
        """
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


class SimpleUsageStore(UsageStore):
    """An element of a store mapping each program variable to its usage status.

    All program variables are *not used* by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: SimpleUsageStore._less_equal
    .. automethod:: SimpleUsageStore._meet
    .. automethod:: SimpleUsageStore._join
    """
    def __init__(self, variables: List[VariableIdentifier]):
        """Map each program variable to its usage status.

        :param variables: list of program variables
        """
        types = [BooleanLyraType, IntegerLyraType, ListLyraType, NdarrayLyraType]
        lattices = {typ: UsageLattice for typ in types}
        super().__init__(variables, lattices)


class SimpleUsageState(Stack, State):
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
        super().__init__(SimpleUsageStore, {'variables': variables})

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
    def _assume(self, condition: Expression) -> 'SimpleUsageState':
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
    def enter_if(self) -> 'SimpleUsageState':
        return self.push()

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'SimpleUsageState':
        return self.pop()

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'SimpleUsageState':
        return self.push()

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'SimpleUsageState':
        return self.pop()

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'SimpleUsageState':
        for identifier in output.ids():
            if isinstance(identifier, VariableIdentifier):
                self.lattice.store[identifier].top()
        return self

    @copy_docstring(State.raise_error)
    def raise_error(self):
        return self

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'SimpleUsageState':
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
