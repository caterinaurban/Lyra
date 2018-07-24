"""
Dictionary Content Analysis
=========================

:Author: Lowis Engel
"""
from copy import deepcopy, copy

from lyra.abstract_domains.data_structures import dict_content_domain
from lyra.abstract_domains.data_structures.dict_content_domain import DictContentState
from lyra.abstract_domains.data_structures.interval_wrappers import IntervalSWrapper, \
    IntervalKWrapper, IntervalVWrapper
from lyra.core.types import BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType, \
    DictLyraType
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.forward import DefaultForwardSemantics


class DictContentAnalysis(Runner):
    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):  # initial state
        # wrapper conversions
        def s_k_conversion(s_state: IntervalSWrapper) -> IntervalKWrapper:
            s_vars = copy(s_state.variables)
            k_var = None
            for var in s_state.variables:
                if var.name == dict_content_domain.k_name:
                    k_var = var
                    s_vars.remove(k_var)
            if not k_var:
                raise ValueError(f"The key variable {dict_content_domain.k_name} "
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
                if var.name == dict_content_domain.v_name:
                    v_var = var
                    s_vars.remove(v_var)
            if not v_var:
                raise ValueError(f"The value variable {dict_content_domain.v_name} "
                                 f"must be added to the scalar store before conversion")
            v_state = IntervalVWrapper(s_vars, v_var)
            v_state._store = deepcopy(s_state.store)

            return v_state

        def v_s_conversion(v_state: IntervalVWrapper) -> IntervalSWrapper:
            vars = copy(v_state.variables)
            s_state = IntervalSWrapper(vars)
            s_state._store = deepcopy(v_state.store)

            return s_state

        scalar_vars = {v for v in self.variables if type(v.typ) in
                       dict_content_domain.scalar_types}
        dict_vars = {v for v in self.variables if type(v.typ) == DictLyraType}
        return DictContentState(IntervalSWrapper, IntervalKWrapper, IntervalVWrapper,
                                scalar_vars, dict_vars,
                                s_k_conversion, k_s_conversion, s_v_conversion, v_s_conversion)