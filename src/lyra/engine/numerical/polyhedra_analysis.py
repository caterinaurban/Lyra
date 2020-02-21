"""
Polyhedra Analysis
==================

:Author: Caterina Urban
"""
from lyra.abstract_domains.numerical.polyhedra_domain import PolyhedraStateWithSummarization
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics


class ForwardPolyhedraAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return PolyhedraStateWithSummarization(self.variables)


class BackwardPolyhedraAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return PolyhedraStateWithSummarization(self.variables)
