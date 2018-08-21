"""
Fulara Usage Analysis
=========================

:Author: Lowis Engel
"""

from lyra.abstract_domains.container.fulara.interval_wrappers import IntervalKWrapper
from lyra.abstract_domains.usage import fulara_usage_domain
from lyra.abstract_domains.usage.fulara_usage_domain import FularaUsageState
from lyra.core.types import DictLyraType
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.container.fulara.fulara_analysis import FularaIntervalAnalysis
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics


class FularaIntervalUsageAnalysis(Runner):
    def interpreter(self):
        forward = ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 2, forward)

    def state(self):  # initial state
        forward = FularaIntervalAnalysis()
        forward._cfg = self.cfg
        init_forward = forward.state()
        scalar_vars = {v for v in self.variables if type(v.typ) in
                       fulara_usage_domain.scalar_types}
        dict_vars = {v for v in self.variables if type(v.typ) == DictLyraType}
        return FularaUsageState(IntervalKWrapper, init_forward, scalar_vars, dict_vars)
