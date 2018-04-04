"""
Input Data Usage Analysis
=========================

:Author: Caterina Urban
"""

from lyra.abstract_domains.usage.usage_domain import UsageState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics


class UsageAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):  # initial state
        return UsageState(self.variables)
