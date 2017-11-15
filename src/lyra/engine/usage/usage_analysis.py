from lyra.abstract_domains.usage.usage_domain import UsageState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.usage.usage_semantics import UsageSemantics


class UsageAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, UsageSemantics(), 3)

    def state(self):
        return UsageState(self.variables)
