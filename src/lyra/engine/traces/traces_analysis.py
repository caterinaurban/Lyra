import ast

from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.abstract_domains.traces.traces_domain import BoolTracesState, TvlTracesState
from lyra.core.expressions import VariableIdentifier


class BoolTracesAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        names = {nd.id for nd in ast.walk(self.tree) if isinstance(nd, ast.Name) and isinstance(nd.ctx, ast.Store)}
        variables = [VariableIdentifier(int, name) for name in names]
        return BoolTracesState(variables, True)


class TvlTracesAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        names = {nd.id for nd in ast.walk(self.tree) if isinstance(nd, ast.Name) and isinstance(nd.ctx, ast.Store)}
        variables = [VariableIdentifier(int, name) for name in names]
        return TvlTracesState(variables, True)
