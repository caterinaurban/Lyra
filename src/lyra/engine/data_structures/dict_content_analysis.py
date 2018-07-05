"""
Dictionary Content Analysis
=========================

:Author: Lowis Engel
"""
from typing import Set

from lyra.abstract_domains.data_structures.dict_content_domain import DictContentState
from lyra.abstract_domains.numerical.interval_domain import IntervalState, IntervalLattice
from lyra.core.types import BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType, \
    DictLyraType
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.forward import DefaultForwardSemantics


class DictContentAnalysis(Runner):
    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):  # initial state
        scalar_types = {BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType}
        scalar_vars = [v for v in self.variables if type(v.typ) in scalar_types]
        dict_vars = [v for v in self.variables if type(v.typ) == DictLyraType]
        return DictContentState(IntervalState, IntervalState, IntervalState, self.interval_decomp, scalar_vars, dict_vars)

    def interval_decomp(self, state: IntervalState, exclude: IntervalState) -> Set[IntervalState]:
        # assert same variables
        left = IntervalState(state.variables)     # left & right non-exclude
        right = IntervalState(state.variables)
        for var in state.variables:
            v_state = state.store[var]
            v_exclude = exclude.store[var]
            if v_state.is_bottom():
                left.store[var].bottom()
                right.store[var].bottom()
            elif v_exclude.is_bottom():
                left.store[var] = IntervalLattice(v_state.lower, v_state.upper)
                right.store[var].bottom()
            else:
                left.store[var] = IntervalLattice(v_state.lower, v_exclude.lower - 1)   # bottom if empty
                right.store[var] = IntervalLattice(v_exclude.upper + 1, v_state.upper)  # bottom if empty

        return {left, right}

