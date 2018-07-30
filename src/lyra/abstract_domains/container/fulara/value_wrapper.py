from abc import ABCMeta, abstractmethod
from copy import copy
from typing import Set

# (Class) Adapter pattern
from lyra.abstract_domains.container.fulara.scalar_wrapper import ScalarWrapper
from lyra.core.expressions import VariableIdentifier


class ValueWrapper(ScalarWrapper, metaclass=ABCMeta):
    """
    (Abstract) wrapper around a domain with some extra functions,
    that are needed for the value state of a DictContentState.
    A concrete wrapper should inherit from this class and the state that should be 'wrapped'.
    """

    def __init__(self, scalar_variables: Set[VariableIdentifier], v_var: VariableIdentifier,
                 *domain_args):
        """
        :param scalar_variables:
        :param v_var: special variable (with correct type)
                      representing the value values at a specific segment
        :param domain_args: arguments needed by the underlying domain
        """
        key_vars = copy(scalar_variables)
        key_vars.add(v_var)
        super().__init__(key_vars, *domain_args)       # init of wrapped domain
        # self._s_vars = copy(scalar_variables)
        self._v_var = v_var

    @property
    def v_var(self) -> VariableIdentifier:
        return self._v_var

    @abstractmethod
    def is_bottom(self) -> bool:
        """Should be true if the special value variable is bottom
        (i.e. cannot have any concrete value)"""
