"""
Interval wrappers for the Fulara Domain
===============================

:Authors: Lowis Engel
"""

from copy import deepcopy, copy
from typing import Set

from lyra.abstract_domains.container.fulara.key_wrapper import KeyWrapper
from lyra.abstract_domains.state import EnvironmentMixin
from lyra.abstract_domains.container.fulara.value_wrapper import ValueWrapper
from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.numerical.interval_domain import IntervalState, IntervalLattice
from lyra.core.expressions import VariableIdentifier
from lyra.core.utils import copy_docstring


class IntervalSWrapper(IntervalState, EnvironmentMixin):
    """Wrapper around IntervalState for scalar domain of FularaState"""

    def __init__(self, scalar_variables: Set[VariableIdentifier]):
        super().__init__(scalar_variables)

    @copy_docstring(EnvironmentMixin.add_variable)
    def add_variable(self, var: VariableIdentifier):
        if var not in self.store.keys():
            self.variables.add(var)
            self.store[var] = IntervalLattice()     # top
        else:
            raise ValueError(f"Variable can not be added to a store if it is already present")

    @copy_docstring(EnvironmentMixin.remove_variable)
    def remove_variable(self, var: VariableIdentifier):
        if var in self.store.keys():
            self.variables.remove(var)
            del self.store[var]
        else:
            raise ValueError(f"Variable can only be removed from a store if it is already present")

    @copy_docstring(EnvironmentMixin.forget_variable)
    def forget_variable(self, var: VariableIdentifier):
        self.store[var].top()


class IntervalKWrapper(KeyWrapper, IntervalSWrapper):
    """Wrapper around IntervalState for key domain of FularaState"""

    def __init__(self, scalar_variables: Set[VariableIdentifier], k_var: VariableIdentifier):
        super().__init__(k_var)
        key_vars = copy(scalar_variables)
        key_vars.add(k_var)
        IntervalSWrapper.__init__(self, key_vars)

    @copy_docstring(KeyWrapper.decomp)
    def decomp(self, exclude: 'IntervalKWrapper') \
            -> Set['IntervalKWrapper']:
        left = deepcopy(self)  # left & right non-exclude
        right = deepcopy(self)

        k_state = self.store[self.k_var]
        k_exclude = exclude.store[self.k_var]
        if k_state.is_bottom():
            left.store[self.k_var].bottom()
            right.store[self.k_var].bottom()
        elif k_exclude.is_bottom():
            left.store[self.k_var] = IntervalLattice(k_state.lower, k_state.upper)
            right.store[self.k_var].bottom()
        elif k_exclude.is_top():  # exclude everything
            left.store[self.k_var].bottom()
            right.store[self.k_var].bottom()
        else:
            left.store[self.k_var] = IntervalLattice(k_state.lower,
                                                     k_exclude.lower - 1)  # bottom if empty
            right.store[self.k_var] = IntervalLattice(k_exclude.upper + 1,
                                                      k_state.upper)  # bottom if empty

        return {left, right}

    @copy_docstring(KeyWrapper.is_singleton)
    def is_singleton(self) -> bool:
        key_interval = self.store[self.k_var]
        return (not key_interval.is_bottom()) and (key_interval.lower == key_interval.upper)

    @copy_docstring(KeyWrapper.__lt__)
    def __lt__(self, other):
        if isinstance(other, IntervalKWrapper):
            s_upper = self.store[self.k_var].upper
            o_lower = other.store[other.k_var].lower
            if s_upper < o_lower:   # other boundaries should conform with interval property by def
                return True
            else:
                return False
        return NotImplemented

    def __repr__(self):
        # other variables do not matter, since it the state is not relational
        return repr(self.store[self.k_var])

    @copy_docstring(KeyWrapper.key_is_bottom)
    def key_is_bottom(self):
        return self.store[self.k_var].is_bottom()


class IntervalVWrapper(ValueWrapper, IntervalSWrapper):
    """Wrapper around IntervalState for value domain of FularaState"""

    def __init__(self, scalar_variables: Set[VariableIdentifier], v_var: VariableIdentifier):
        super().__init__(v_var)
        value_vars = copy(scalar_variables)
        value_vars.add(v_var)
        IntervalSWrapper.__init__(self, value_vars)

    def __repr__(self):
        # other variables do not matter, since it the state is not relational
        return repr(self.store[self.v_var])

    @copy_docstring(ValueWrapper.value_is_bottom)
    def value_is_bottom(self):
        return self.store[self.v_var].is_bottom()
