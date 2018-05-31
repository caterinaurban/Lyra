"""
Input Data Usage Analysis
=========================

:Author: Caterina Urban
"""

from lyra.abstract_domains.usage.usage_domain import SimpleUsageState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics


class SimpleUsageAnalysis(Runner):

    def interpreter(self):
        state = SimpleUsageState(self.variables)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3, state)
