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

from lyra.abstract_domains.numerical.interval_domain import IntervalStateWithSummarization, \
    BoxStateWithSummarization, IntervalStateWithIndexing


class ForwardIntervalAnalysisWithSummarization(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return IntervalStateWithSummarization(self.variables)


class ForwardIntervalAnalysisWithIndexing(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        IntervalStateWithIndexing.bound = 3
        return IntervalStateWithIndexing(self.variables)


class ForwardBoxAnalysisWithSummarization(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return BoxStateWithSummarization(self.variables)


class BackwardIntervalAnalysisWithSummarization(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return IntervalStateWithSummarization(self.variables)


class BackwardBoxAnalysisWithSummarization(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return BoxStateWithSummarization(self.variables)
