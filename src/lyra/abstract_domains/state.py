"""
Abstract Domain
===============

Interface of an abstract domain.
Abstract domain elements support lattice operations and program statements.

:Author: Caterina Urban
"""


from abc import ABCMeta, abstractmethod
from collections import defaultdict
from copy import deepcopy
from typing import Set, Optional, List, Type, Dict, Any, Union

from lyra.abstract_domains.lattice import Lattice
from lyra.core.expressions import Expression, VariableIdentifier, Subscription, Slicing, AttributeReference
from lyra.core.statements import ProgramPoint
from lyra.core.utils import copy_docstring


class State(Lattice, metaclass=ABCMeta):
    """Analysis state. A mutable element of an abstract domain.

    .. warning::
        Lattice operations and statements modify the current state.
    """

    def __init__(self, precursory: 'State' = None):
        super().__init__()
        self._result = set()
        self._pp = None
        self._precursory = precursory

    @property
    def result(self):
        """Result of the previously analyzed statement."""
        return self._result

    @result.setter
    def result(self, result: Set[Expression]):
        self._result = result

    @property
    def pp(self):
        """Program point of the currently analyzed statement."""
        return self._pp

    @pp.setter
    def pp(self, pp: ProgramPoint):
        self._pp = pp

    @property
    def precursory(self):
        """Current precursory analysis state."""
        return self._precursory

    @precursory.setter
    def precursory(self, precursory: 'State'):
        self._precursory = precursory

    def __repr__(self):
        return ", ".join("{}".format(expression) for expression in self.result)

    @abstractmethod
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'State':
        """Assign an expression to a variable identifier

        :param left: the variable identifier to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """

    @abstractmethod
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'State':
        """Assign an expression to a subscription

        :param left: the subscription to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """

    @abstractmethod
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'State':
        """Assign an expression to a slicing

        :param left: the slicing to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """

    def _assign(self, left: Expression, right: Expression) -> 'State':
        """Assign an expression to another expression.

        .. warning::
            The current state could also be bottom or top.

        :param left: expression to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment

        """
        if isinstance(left, VariableIdentifier):
            return self._assign_variable(left, right)
        elif isinstance(left, AttributeReference):
            raise NotImplementedError(f"Assignment to attribute reference {left} is unsupported!")
        elif isinstance(left, Subscription):
            return self._assign_subscription(left, right)
        elif isinstance(left, Slicing):
            return self._assign_slicing(left, right)
        raise ValueError(f"Unexpected assignment to {left}!")

    def assign(self, left: Set[Expression], right: Set[Expression]) -> 'State':
        """Assign an expression to another expression.

        :param left: set of expressions representing the expression to be assigned to
        :param right: set of expressions representing the expression to assign
        :return: current state modified by the assignment

        """
        self.big_join([deepcopy(self)._assign(lhs, rhs) for lhs in left for rhs in right])
        self.result = set()  # assignments have no result, only side-effects
        return self

    @abstractmethod
    def _assume(self, condition: Expression, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        .. warning::
            The current state could also be bottom or top.

        :param condition: expression representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    def assume(self, condition: Set[Expression], bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: set of expressions representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """
        self.big_join([deepcopy(self)._assume(expr, bwd=bwd) for expr in condition])
        return self

    def before(self, pp: ProgramPoint, precursory: Optional['State']) -> 'State':
        """Set the program point of the currently analyzed statement
        and the current precursory analysis state.

        :param pp: current program point
        :param precursory: current precursory analysis state
        :return: current state modified to set the current program point and precursory state
        """
        self.pp = pp
        self.precursory = precursory
        return self

    @abstractmethod
    def enter_if(self) -> 'State':
        """Enter a conditional if statement.

        .. warning::
            The current state could also be bottom or top.

        :return: current state modified to enter a conditional if statement

        """

    @abstractmethod
    def exit_if(self) -> 'State':
        """Exit a conditional if statement.

        .. warning::
            The current state could also be bottom or top.

        :return: current state modified to enter a conditional if statement

        """

    @abstractmethod
    def enter_loop(self) -> 'State':
        """Enter a loop.

        .. warning::
            The current state could also be bottom or top.

        :return: current state modified to enter a loop

        """

    @abstractmethod
    def exit_loop(self) -> 'State':
        """Exit a loop.

        .. warning::
            The current state could also be bottom or top.

        :return: current state modified to exit a loop

        """

    def filter(self, bwd: bool = False) -> 'State':
        """Assume that the current result holds in the current state.

        :param bwd: whether the filtering happens in a backward analysis (default: False)
        :return: current state modified to satisfy the current result

        """
        self.assume(self.result, bwd=bwd)
        self.result = set()  # filtering has no result, only side-effects
        return self

    @abstractmethod
    def forget_variable(self, variable: VariableIdentifier) -> 'State':
        """Forget a variable value.

        :param variable: variable whose value is to be forgotten
        :return: current state modified to have forgotten the given variable value
        """

    @abstractmethod
    def _output(self, output: Expression) -> 'State':
        """Outputs something in the current state.

        .. warning::
            The current state could also be bottom or top.

        :param output: expression representing the output
        :return: current state modified by the output

        """

    def output(self, output: Set[Expression]) -> 'State':
        """Outputs something in the current state.

        :param output: set of expressions representing the output
        :return: current state modified by the output

        """
        self.big_join([deepcopy(self)._output(expr) for expr in output])
        self.result = set()  # outputs have no result, only side-effects
        return self

    def raise_error(self) -> 'State':
        """Raise an error.

        :return: current state modified to be the bottom state
        """
        return self.bottom()

    @abstractmethod
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'State':
        """substitute an expression to a variable identifier

        :param left: the variable identifier to be substituted to
        :param right: expression to substitute
        :return: current state modified by the substitution
        """

    @abstractmethod
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'State':
        """substitute an expression to a subscription

        :param left: the subscription to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution
        """

    @abstractmethod
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'State':
        """substitute an expression to a slicing

        :param left: the slicing to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution
        """

    def _substitute(self, left: Expression, right: Expression) -> 'State':
        """Substitute an expression to another expression.

        .. warning::
            The current state could also be bottom or top.

        :param left: expression to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution

        """
        if isinstance(left, VariableIdentifier):
            return self._substitute_variable(left, right)
        elif isinstance(left, AttributeReference):
            raise NotImplementedError(f"Substitution of attribute reference {left} is unsupported!")
        elif isinstance(left, Subscription):
            return self._substitute_subscription(left, right)
        elif isinstance(left, Slicing):
            return self._substitute_slicing(left, right)
        raise ValueError(f"Unexpected substitution of {left}!")

    def substitute(self, left: Set[Expression], right: Set[Expression]) -> 'State':
        """Substitute an expression to another expression.

        :param left: set of expressions representing the expression to be substituted
        :param right: set of expressions representing the expression to substitute
        :return: current state modified by the substitution

        """
        self.big_join([deepcopy(self)._substitute(l, r) for l in left for r in right])
        self.result = set()  # assignments have no result, only side-effects
        return self


class StateWithSummarization(State, metaclass=ABCMeta):

    def _assign_summary(self, left: Union[Subscription, Slicing], right: Expression) -> 'StateWithSummarization':
        """Assign an expression to a summary variable.

        :param left: summary variable to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """
        # copy the current state
        current: StateWithSummarization = deepcopy(self)
        # perform the substitution on the copy of the current state
        self._assign_variable(left.target, right)
        # perform a weak update on the current state
        return self.join(current)

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'StateWithSummarization':
        return self._assign_summary(left, right)

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'StateWithSummarization':
        return self._assign_summary(left, right)

    def _substitute_summary(self, left: Union[Subscription, Slicing], right: Expression) -> 'StateWithSummarization':
        """Substitute an expression to a summary variable.

        :param left: summary variable to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution
        """
        # copy the current state
        current: StateWithSummarization = deepcopy(self)
        # perform the substitution on the copy of the current state
        self._substitute_variable(left.target, right)
        # check for errors turning the state into bottom
        if self.is_bottom():
            return self
        # if there are not errors, perform a weak update on the current state
        return self.join(current)

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'StateWithSummarization':
        return self._substitute_summary(left, right)

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'StateWithSummarization':
        return self._substitute_summary(left, right)


class ProductState(State):
    """Product analysis state. A mutable element of a product abstract domain.
    (MRO: ProductState, State, Lattice)
    
    .. warning::
        Lattice operations and statements modify the current state.
    """

    def __init__(self, states: List[Type[State]], arguments=None, precursory: State = None):
        super().__init__(precursory)
        if arguments is None:
            arguments: Dict[Type, Dict[str, Any]] = defaultdict(lambda: dict())
        self._states = [state(**arguments[state]) for state in states]

    @property
    def states(self):
        """Current list of states."""
        return self._states
    
    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return "\n".join(str(state) for state in self.states)

    @copy_docstring(State.bottom)
    def bottom(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.bottom()
        return self

    @copy_docstring(State.top)
    def top(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.top()
        return self

    @copy_docstring(State.is_bottom)
    def is_bottom(self) -> bool:
        return any(state.is_bottom() for state in self.states)

    @copy_docstring(State.is_top)
    def is_top(self) -> bool:
        return all(state.is_top() for state in self.states)

    @copy_docstring(State._less_equal)
    def _less_equal(self, other: 'ProductState') -> bool:
        return all(state.less_equal(other.states[i]) for i, state in enumerate(self.states))

    @copy_docstring(State._join)
    def _join(self, other: 'ProductState') -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.join(other.states[i])
        return self

    @copy_docstring(State._meet)
    def _meet(self, other: 'ProductState'):
        for i, state in enumerate(self.states):
            self.states[i] = state.meet(other.states[i])
        return self

    @copy_docstring(State._widening)
    def _widening(self, other: 'ProductState'):
        for i, state in enumerate(self.states):
            self.states[i] = state.widening(other.states[i])
        return self

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assign_variable(left, right)
        return self

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assign_subscription(left, right)
        return self

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assign_slicing(left, right)
        return self

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume(condition, bwd=bwd)
        return self

    @copy_docstring(State.before)
    def before(self, pp: ProgramPoint, precursory: Optional['State']) -> 'ProductState':
        super().before(pp, precursory)
        for i, state in enumerate(self.states):
            self.states[i] = state.before(pp, precursory)
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.enter_if()
        return self

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.exit_if()
        return self

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.enter_loop()
        return self

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.exit_loop()
        return self

    @copy_docstring(State.forget_variable)
    def forget_variable(self, variable: VariableIdentifier) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.forget_variable(variable)
        return self

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.output({output})
        return self

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._substitute_variable(left, right)
        return self

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._substitute_subscription(left, right)
        return self

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._substitute_slicing(left, right)
        return self
