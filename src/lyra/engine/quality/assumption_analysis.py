from lyra.abstract_domains.quality.assumption_domain import AssumptionState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics


class AssumptionAnalysis(Runner):

    def __init__(self, do_render=True, show_simple=False):
        super().__init__()
        self.do_render = do_render
        self.show_simple = show_simple

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return AssumptionState(self.variables)

    def run(self):
        result = self.interpreter().analyze(self.state())
        if self.show_simple:
            for node, items in result.result.items():
                if node.identifier == 1:
                    items[0] = items[0].stack_top.assmps
        if self.do_render:
            self.render(result)
        return result
