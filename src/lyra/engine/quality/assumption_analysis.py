from lyra.abstract_domains.quality.assumption_domain import AssumptionState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics


class AssumptionAnalysis(Runner):

    def __init__(self, do_render=True):
        super().__init__()
        self.do_render = do_render

    def interpreter(self):
        state = AssumptionState(self.variables)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3, state)

    def render(self, result):
        if self.do_render:
            super().render(result)
