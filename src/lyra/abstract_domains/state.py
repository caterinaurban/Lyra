"""
Abstract Domain
===============

Interface of an abstract domain.
Abstract domain elements support lattice operations and program statements.

:Author: Caterina Urban
"""


from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import Set, Optional

from lyra.abstract_domains.lattice import Lattice
from lyra.core.expressions import Expression, VariableIdentifier
from lyra.core.statements import ProgramPoint


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
    def _assign(self, left: Expression, right: Expression) -> 'State':
        """Assign an expression to another expression.

        :param left: expression to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment

        """

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
    def _assume(self, condition: Expression) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: expression representing the assumed condition
        :return: current state modified to satisfy the assumption

        """

    def assume(self, condition: Set[Expression]) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: set of expressions representing the assumed condition
        :return: current state modified to satisfy the assumption

        """
        self.big_join([deepcopy(self)._assume(expr) for expr in condition])
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

        :return: current state modified to enter a conditional if statement

        """

    @abstractmethod
    def exit_if(self) -> 'State':
        """Exit a conditional if statement.

        :return: current state modified to enter a conditional if statement

        """

    @abstractmethod
    def enter_loop(self) -> 'State':
        """Enter a loop.

        :return: current state modified to enter a loop

        """

    @abstractmethod
    def exit_loop(self) -> 'State':
        """Exit a loop.

        :return: current state modified to exit a loop

        """

    def filter(self) -> 'State':
        """Assume that the current result holds in the current state.

        :return: current state modified to satisfy the current result

        """
        self.assume(self.result)
        self.result = set()  # filtering has no result, only side-effects
        return self

    @abstractmethod
    def _output(self, output: Expression) -> 'State':
        """Outputs something in the current state.

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
    def _substitute(self, left: Expression, right: Expression) -> 'State':
        """Substitute an expression to another expression.

        :param left: expression to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution

        """

    def substitute(self, left: Set[Expression], right: Set[Expression]) -> 'State':
        """Substitute an expression to another expression.

        :param left: set of expressions representing the expression to be substituted
        :param right: set of expressions representing the expression to substitute
        :return: current state modified by the substitution

        """
        self.big_join([deepcopy(self)._substitute(l, r) for l in left for r in right])
        self.result = set()  # assignments have no result, only side-effects
        return self


class EnvironmentMixin(State, metaclass=ABCMeta):
    """Mixin to add environment modification operations to a state."""

    @abstractmethod
    def add_variable(self, variable: VariableIdentifier):
        """Adds a new variable to the state with no information about it (top)"""

    @abstractmethod
    def remove_variable(self, variable: VariableIdentifier):
        """Removes a variable from the state"""

    @abstractmethod
    def forget_variable(self, variable: VariableIdentifier):
        """Forgets everything about variable -> sets to top"""
