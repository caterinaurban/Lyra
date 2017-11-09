import ast

from lyra.core.types import IntegerLyraType
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.core.expressions import VariableIdentifier


class IntervalAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)
        # return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        names = {nd.id for nd in ast.walk(self.tree) if isinstance(nd, ast.Name) and isinstance(nd.ctx, ast.Store)}
        variables = [VariableIdentifier(IntegerLyraType(), name) for name in names]
        return IntervalState(variables)
