"""
Interval Analysis
=================

:Author: Caterina Urban
"""

from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.interval_domain import IntervalState, BoxStateWithSummarization


class ForwardIntervalAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return IntervalState(self.variables)


class ForwardBoxAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return BoxStateWithSummarization(self.variables)


class BackwardIntervalAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return IntervalState(self.variables)


class BackwardBoxAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return BoxStateWithSummarization(self.variables)
