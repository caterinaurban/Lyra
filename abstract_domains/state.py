from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import Set

from abstract_domains.lattice import Lattice
from core.cfg import Edge
from core.expressions import Expression, VariableIdentifier
from core.statements import ProgramPoint


class State(Lattice, metaclass=ABCMeta):
    def __init__(self):
        """Analysis state representation. 
        Account for lattice operations and statement effects by modifying the current state.
        """
        super().__init__()
        self._result = set()  # set of expressions representing the result of the previously analyzed statement

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result: Set[Expression]):
        self._result = result

    def __repr__(self):
        """Unambiguous string representing the current state.

        :return: unambiguous representation string
        """
        return ", ".join("{}".format(expression) for expression in self.result)

    @abstractmethod
    def _access_variable(self, variable: VariableIdentifier) -> Set[Expression]:
        """Retrieve a variable value. Account for side-effects by modifying the current state. 
        
        :param variable: variable to retrieve the value of
        :return: set of expressions representing the variable value
        """

    def access_variable(self, variable: VariableIdentifier) -> 'State':
        """Access a variable.
        
        :param variable: variable to be accesses
        :return: current state modified by the variable access
        """
        self.result = self._access_variable(variable)
        return self

    @abstractmethod
    def _assign_variable(self, left: Expression, right: Expression) -> 'State':
        """Assign an expression to a variable.
        
        :param left: expression representing the variable to be assigned to 
        :param right: expression to assign
        :return: current state modified by the variable assignment
        """

    def assign_variable(self, left: Set[Expression], right: Set[Expression]) -> 'State':
        """Assign an expression to a variable.
        
        :param left: set of expressions representing the variable to be assigned to
        :param right: set of expressions representing the expression to assign
        :return: current state modified by the variable assignment
        """
        self.big_join([deepcopy(self)._assign_variable(lhs, rhs) for lhs in left for rhs in right])
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

    @abstractmethod
    def _evaluate_literal(self, literal: Expression) -> Set[Expression]:
        """Retrieve a literal value. Account for side-effects by modifying the current state.

        :param literal: literal to retrieve the value of
        :return: set of expressions representing the literal value
        """

    def evaluate_literal(self, literal: Expression) -> 'State':
        """Evaluate a literal.

        :param literal: expression to be evaluated
        :return: current state modified by the literal evaluation
        """
        self.result = self._evaluate_literal(literal)
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

    @abstractmethod
    def _substitute_variable(self, left: Expression, right: Expression, *args, **kwargs) -> 'State':
        """Substitute an expression to a variable.

        :param left: expression representing the variable to be substituted
        :param right: expression to substitute
        :return: current state modified by the variable substitution
        """

    def substitute_variable(self, left: Set[Expression], right: Set[Expression], *args, **kwargs) -> 'State':
        """Substitute an expression to a variable.
        
        :param left: set of expressions representing the variable to be substituted
        :param right: set of expressions representing the expression to substitute
        :return: current state modified by the variable substitution
        """
        self.big_join([deepcopy(self)._substitute_variable(lhs, rhs, *args, **kwargs) for lhs in left for rhs in right])
        self.result = set()  # assignments have no result, only side-effects
        return self

    def next(self, pp: ProgramPoint, edge_kind: Edge.Kind = None):
        """Called by the engine *before* **(time-wise)** the statement at a program point gets interpreted.
        
        If the engine runs a forward analysis, this state is considered to be *before* **(in situ)** the program 
        point ``pp`` interpreted next. Otherwise in a backwards analysis, this state is considered to be *after*
        **(in situ)** the program point ``pp`` interpreted next. 
        
        :param pp: the program point of the statement interpreted next
        :param edge_kind: the kind of edge just passed in case the next statement is a conditional, otherwise ``None``
        """
        pass
