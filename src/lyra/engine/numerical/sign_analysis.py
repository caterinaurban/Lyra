"""
Sign Analysis
=============

:Author: Jérôme Dohrau and Caterina Urban
"""
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics
from lyra.abstract_domains.numerical.sign_domain import SignState


class ForwardSignAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):
        return SignState(self.variables)


class BackwardSignAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return SignState(self.variables)
