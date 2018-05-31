"""
Interval analysis
=================

:Author: Caterina Urban
"""

from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.interval_domain import IntervalState


class ForwardIntervalAnalysis(Runner):

    def interpreter(self):
        state = IntervalState(self.variables)
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3, state)


class BackwardIntervalAnalysis(Runner):

    def interpreter(self):
        state = IntervalState(self.variables)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3, state)
