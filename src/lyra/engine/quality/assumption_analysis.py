from typing import List

from lyra.abstract_domains.quality.assumption_domain import AssumptionState
from lyra.core.expressions import LengthIdentifier, Identifier
from lyra.core.types import ListLyraType, StringLyraType
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics


class AssumptionAnalysis(Runner):

    def __init__(self, do_render=True, show_simple=False):
        super().__init__()
        self.do_render = do_render
        self.show_simple = show_simple

    @property
    def variables(self) -> List[Identifier]:
        all_vars = super().variables
        for var in all_vars:
            if isinstance(var.typ, ListLyraType):
                length_var = LengthIdentifier(var)
                if length_var in all_vars:
                    continue
                all_vars.append(length_var)
        return all_vars

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
