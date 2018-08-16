"""
Fulara Analysis
=========================

:Author: Lowis Engel
"""
from copy import deepcopy, copy

from lyra.abstract_domains.container.fulara import fulara_domain
from lyra.abstract_domains.container.fulara.fulara_domain import FularaState
from lyra.abstract_domains.container.fulara.interval_wrappers import IntervalSWrapper, \
    IntervalKWrapper, IntervalVWrapper
from lyra.core.types import DictLyraType
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.forward import DefaultForwardSemantics


class FularaAnalysis(Runner):
    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):  # initial state
        # wrapper conversions
        def s_k_conversion(s_state: IntervalSWrapper) -> IntervalKWrapper:
            s_vars = copy(s_state.variables)
            k_var = None
            for var in s_state.variables:
                if var.name == fulara_domain.k_name:
                    k_var = var
                    s_vars.remove(k_var)
            if not k_var:
                raise ValueError(f"The key variable {fulara_domain.k_name} "
                                 f"must be added to the scalar store before conversion")
            k_state = IntervalKWrapper(s_vars, k_var)
            k_state._store = deepcopy(s_state.store)

            return k_state

        def k_s_conversion(k_state: IntervalKWrapper) -> IntervalSWrapper:
            vars = copy(k_state.variables)
            s_state = IntervalSWrapper(vars)
            s_state._store = deepcopy(k_state.store)

            return s_state

        def s_v_conversion(s_state: IntervalSWrapper) -> IntervalVWrapper:
            s_vars = copy(s_state.variables)
            v_var = None
            for var in s_state.variables:
                if var.name == fulara_domain.v_name:
                    v_var = var
                    s_vars.remove(v_var)
            if not v_var:
                raise ValueError(f"The value variable {fulara_domain.v_name} "
                                 f"must be added to the scalar store before conversion")
            v_state = IntervalVWrapper(s_vars, v_var)
            v_state._store = deepcopy(s_state.store)

            return v_state

        def v_s_conversion(v_state: IntervalVWrapper) -> IntervalSWrapper:
            vars = copy(v_state.variables)
            s_state = IntervalSWrapper(vars)
            s_state._store = deepcopy(v_state.store)

            return s_state

        def update_k_from_scalar(k_state: IntervalKWrapper, s_state: IntervalSWrapper) -> IntervalKWrapper:
            result = deepcopy(k_state)
            for var in s_state.store:
                result.store[var] = deepcopy(s_state.store[var])
            return result

        def update_v_from_scalar(v_state: IntervalVWrapper, s_state: IntervalSWrapper) -> IntervalVWrapper:
            result = deepcopy(v_state)
            for var in s_state.store:
                result.store[var] = deepcopy(s_state.store[var])
            return result

        scalar_vars = {v for v in self.variables if type(v.typ) in
                       fulara_domain.scalar_types}
        dict_vars = {v for v in self.variables if type(v.typ) == DictLyraType}
        return FularaState(IntervalSWrapper, IntervalKWrapper, IntervalVWrapper,
                           update_k_from_scalar, update_v_from_scalar,
                           scalar_vars, dict_vars,
                           s_k_conversion, k_s_conversion, s_v_conversion, v_s_conversion)
