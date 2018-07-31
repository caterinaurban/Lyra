from abc import ABCMeta, abstractmethod
from typing import Set

from lyra.abstract_domains.state import State
from lyra.core.expressions import VariableIdentifier

# def __init__(self, scalar_variables: Set[VariableIdentifier], *domain_args):
#     """
#     :param scalar_variables: set of variables the state should range over
#     :param domain_args: arguments needed by the underlying domain
#     """
#     super().__init__(scalar_variables, *domain_args)      # init of wrapped domain
