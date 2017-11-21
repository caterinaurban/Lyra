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
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):
        return IntervalState(self.variables)


class BackwardIntervalAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return IntervalState(self.variables)
