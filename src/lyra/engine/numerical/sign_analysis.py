"""
Sign Analysis
=============

:Author: Jerome Dohrau
"""

from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.sign_domain import SignState


class ForwardSignAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):
        return SignState(self.variables)
