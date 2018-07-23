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
        :param scalar_variables: set of variables the state should range over (all scalar variables)
        :param domain_args: arguments needed by the underlying domain
        """
        super().__init__(scalar_variables, *domain_args)      # init of wrapped domain

    @abstractmethod
    def add_var(self, var: VariableIdentifier):
        """Adds a new variable to the state with no information about it (top)"""

    @abstractmethod
    def remove_var(self, var: VariableIdentifier):
        """Removes a variable from the state"""

    @abstractmethod
    def invalidate_var(self, var: VariableIdentifier):
        """Forgets everything about var -> sets to top"""
