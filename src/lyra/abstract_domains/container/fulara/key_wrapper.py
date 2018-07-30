from abc import ABCMeta, abstractmethod
from copy import copy

from typing import Set


# (Class) Adapter pattern
from lyra.abstract_domains.container.fulara.scalar_wrapper import ScalarWrapper
from lyra.core.expressions import VariableIdentifier


class KeyWrapper(ScalarWrapper, metaclass=ABCMeta):
    """
    (Abstract) wrapper around a domain with some extra functions,
    that are needed for the key state of a DictContentState.
    A concrete wrapper should inherit from this class and the state that should be 'wrapped'.
    """

    def __init__(self, scalar_variables: Set[VariableIdentifier], k_var: VariableIdentifier,
                 *domain_args):
        """
        :param scalar_variables:
        :param k_var: special variable (with correct type)
                      representing the key values at a specific segment
        :param domain_args: arguments needed by the underlying domain
        """
        key_vars = copy(scalar_variables)
        key_vars.add(k_var)
        super().__init__(key_vars, *domain_args)       # init of wrapped domain
        # self._s_vars = copy(scalar_variables)
        self._k_var = k_var

    @property
    def k_var(self) -> VariableIdentifier:
        return self._k_var

    # @property
    # def s_vars(self) -> Set[VariableIdentifier]:
    #     return self._s_vars

    @abstractmethod
    def is_singleton(self) -> bool:
        """
        Returns true, if in the current state k_var represents a single concrete value.
        (needed for strong updates)
        """

    @abstractmethod
    def decomp(self, state: 'KeyWrapper', exclude: 'KeyWrapper') -> Set['KeyWrapper']:
        """
        Computes a decomposition/partition of the given state into a set of rest states,
        excluding all parts that overlap (meet not bottom) with the 'exclude' state.
        i.e.: 'subtracts the meet of state & exclude from state'
        :param state: (current) state to be decomposed
        :param exclude: parts to be excluded
        :return: decomposition/partition of 'state' avoiding 'exclude'
        """

    @abstractmethod
    def __lt__(self, other):
        """Used to order disjoint segements for their unique representation.
        Does not (need to) conform with Lattice's less_equal"""

    @abstractmethod
    def is_bottom(self) -> bool:
        """Should be true if the special key variable is bottom
        (i.e. cannot have any concrete value)"""
