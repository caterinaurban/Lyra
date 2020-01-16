"""
Octagon Analysis
================

:Author: Caterina Urban
"""
from lyra.abstract_domains.numerical.octagon_domain import OctagonStateWithSummarization
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics


class ForwardOctagonAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return OctagonStateWithSummarization(self.variables)


class BackwardOctagonAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return OctagonStateWithSummarization(self.variables)
