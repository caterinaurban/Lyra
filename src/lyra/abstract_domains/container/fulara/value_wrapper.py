from abc import ABCMeta, abstractmethod
from copy import copy
from typing import Set

# (Class) Adapter pattern
from lyra.abstract_domains.state import EnvironmentMixin
from lyra.core.expressions import VariableIdentifier


class ValueWrapper(EnvironmentMixin, metaclass=ABCMeta):
    """
    (Abstract) wrapper around a domain with some extra functions,
    that are needed for the value state of a FularaState.
    A concrete wrapper should inherit from this class and the state that should be 'wrapped'.
    """

    def __init__(self, v_var: VariableIdentifier):
        """
        :param v_var: special variable (with correct type)
                      representing the value values at a specific segment
        """
        EnvironmentMixin.__init__(self)
        self._v_var = v_var

    @property
    def v_var(self) -> VariableIdentifier:
        return self._v_var

    @abstractmethod
    def is_bottom(self) -> bool:
        """Should be true if the special value variable is bottom
        (i.e. cannot have any concrete value)"""
