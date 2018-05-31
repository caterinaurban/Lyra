"""
(Strongly) Live Variable Analysis
=================================

:Author: Caterina Urban
"""

from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.abstract_domains.liveness.liveness_domain import LivenessState, StrongLivenessState


class LivenessAnalysis(Runner):

    def interpreter(self):
        state = LivenessState(self.variables)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3, state)


class StrongLivenessAnalysis(Runner):

    def interpreter(self):
        state = StrongLivenessState(self.variables)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3, state)
