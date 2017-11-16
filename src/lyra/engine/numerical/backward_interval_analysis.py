import ast

from lyra.abstract_domains.numerical.interval_domain import IntervalDomain, IntervalLattice, Interval
from lyra.core.expressions import VariableIdentifier
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics


class BackwardIntervalAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        names = {nd.id for nd in ast.walk(self.tree) if isinstance(nd, ast.Name) and isinstance(nd.ctx, ast.Store)}
        variables = [VariableIdentifier(int, name) for name in names]
        domain = IntervalDomain(variables)
        return domain
