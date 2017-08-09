from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import Set

from abstract_domains.lattice import BoundedLattice, Lattice
from abstract_domains.state import State
from core.cfg import Edge
from core.expressions import VariableIdentifier, Expression, Index
from core.statements import ProgramPoint


class Stack(BoundedLattice, metaclass=ABCMeta):
    """A stack of elements of a lattice L."""

    def __init__(self, initial_element: Lattice):
        """Create a stack of lattice elements.
        
        Initially there is only the ``initial_element`` on the stack.

        :param initial_element: the initial element on the stack
        """
        super().__init__()
        self._stack = [initial_element]

    @property
    def stack(self):
        return self._stack

    def __repr__(self):
        return " | ".join(map(repr, self.stack))

    @abstractmethod
    def push(self):
        """Push an element on the stack."""

    @abstractmethod
    def pop(self):
        """Pop an element from the stack."""

    def _less_equal(self, other: 'Stack') -> bool:
        if len(self.stack) != len(other.stack):
            raise Exception("Stacks must be equally long")
        return all(l.less_equal(r) for l, r in zip(self.stack, other.stack))

    def _join(self, other: 'Stack') -> 'Stack':
        if len(self.stack) != len(other.stack):
            raise Exception("Stacks must be equally long")
        for i, item in enumerate(self.stack):
            item.join(other.stack[i])
        return self

    def _meet(self, other: 'Stack'):
        if len(self.stack) != len(other.stack):
            raise Exception("Stacks must be equally long")
        for i, item in enumerate(self.stack):
            item.meet(other.stack[i])
        return self

    def _widening(self, other: 'Stack'):
        return self._join(other)


class ScopeDescendCombineMixin:
    @abstractmethod
    def descend(self) -> 'ScopeDescendCombineMixin':
        """Called when this state descends into deeper nested scope."""

    @abstractmethod
    def combine(self, other: 'ScopeDescendCombineMixin') -> 'ScopeDescendCombineMixin':
        """Called when this state ascends into upper scope."""


class ScopeStack(Stack, State):
    def __init__(self, initial_element: Lattice):
        """A specialized stack domain that has a notion of scopes.

        :param initial_element: initial element
        """
        super().__init__(initial_element)
        self._postponed_pushpop = []  # postponed stack pushs/pops that are later executed in ``_assume()``

    def __repr__(self):
        # change default stack representation to only show top level frame
        return ("... | " if len(self.stack) > 1 else "") + repr(self.stack[-1])

    def push(self):
        if self.is_bottom():
            return self
        self.stack.append(deepcopy(self.stack[-1]).descend())
        return self

    def pop(self):
        if self.is_bottom():
            return self
        popped = self.stack.pop()
        self.stack[-1].combine(popped)
        return self

    def _access_variable(self, variable: VariableIdentifier) -> Set[Expression]:
        self.stack[-1].access_variable(variable)
        return {variable}

    def _assign_variable(self, left: Expression, right: Expression) -> 'DescendCombineStackDomain':
        raise NotImplementedError("Variable assignment is not supported!")

    def _assume(self, condition: Expression) -> 'DescendCombineStackDomain':
        # only update used variable in conditional edge via assume call to store
        # if we are on a loop/if exit edge!!
        if self._postponed_pushpop:
            self.stack[-1].assume({condition})

        # make good for postponed push/pop, since that was postponed until assume has been applied to top frame
        # (the engine implements a different order of calls to exit_if/exit_loop and assume than we want)
        for pushpop in self._postponed_pushpop:
            pushpop()
        self._postponed_pushpop.clear()

        return self

    def _evaluate_literal(self, literal: Expression) -> Set[Expression]:
        self.stack[-1].evaluate_literal(literal)
        return {literal}

    def _postponed_exit_if(self):
        if self.is_bottom():
            return self
        self.pop()
        return self

    def enter_loop(self):
        return self.enter_if()

    def exit_loop(self):
        return self.exit_if()

    def enter_if(self):
        if self.is_bottom():
            return self
        self.push()
        return self

    def exit_if(self):
        self._postponed_pushpop.append(self._postponed_exit_if)
        return self

    def _output(self, output: Expression) -> 'DescendCombineStackDomain':
        if self.is_bottom():
            return self
        self.stack[-1].output({output})
        return self

    def _substitute_variable(self, left: Expression, right: Expression) -> 'DescendCombineStackDomain':
        if isinstance(left, (VariableIdentifier, Index)):
            self.stack[-1].substitute_variable({left}, {right})
        else:
            raise NotImplementedError("Variable substitution for {} is not implemented!".format(left))
        return self

    def next(self, pp: ProgramPoint, edge_kind: Edge.Kind = None):
        self.stack[-1].next(pp, edge_kind)
