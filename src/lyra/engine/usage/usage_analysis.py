import ast

from lyra.core.expressions import VariableIdentifier
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner

from lyra.abstract_domains.usage.stack import UsedStack
from lyra.semantics.usage.usage_semantics import UsageSemantics


class UsageAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, UsageSemantics(), 3)

    def state(self):
        names = {nd.id for nd in ast.walk(self.tree) if isinstance(nd, ast.Name) and isinstance(nd.ctx, ast.Store)}
        variables = [VariableIdentifier(int, name) for name in names]
        return UsedStack(variables)
