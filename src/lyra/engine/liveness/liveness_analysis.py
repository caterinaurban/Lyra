from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.abstract_domains.liveness.liveness_domain import LivenessState


class LivenessAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return LivenessState(self.variables)
