from abc import ABCMeta, abstractmethod
from typing import Set

from lyra.core.expressions import VariableIdentifier


# (Class) Adapter pattern
class ScalarWrapper(metaclass=ABCMeta):
    """
    (Abstract) wrapper around a domain with some extra functions,
    that are needed for the scalar state of a DictContentState.
    A concrete wrapper should inherit from this class and the state that should be 'wrapped'.
    """

    def __init__(self, scalar_variables: Set[VariableIdentifier], *domain_args):
        """
        :param scalar_variables: set of variables the state should range over
        :param domain_args: arguments needed by the underlying domain
        """
        super().__init__(scalar_variables, *domain_args)      # init of wrapped domain

    @abstractmethod
    def add_variable(self, variable: VariableIdentifier):
        """Adds a new variable to the state with no information about it (top)"""

    @abstractmethod
    def remove_variable(self, variable: VariableIdentifier):
        """Removes a variable from the state"""

    @abstractmethod
    def forget_variable(self, variable: VariableIdentifier):
        """Forgets everything about variable -> sets to top"""
