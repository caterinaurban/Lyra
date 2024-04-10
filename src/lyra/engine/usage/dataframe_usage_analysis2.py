from lyra.abstract_domains.usage.dataframe_usage_domain2 import DataFrameColumnUsageState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.dataframe_usage_semantics import DataFrameColumnUsageSemantics


class DataFrameColumnUsageAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DataFrameColumnUsageSemantics(), 3)

    def state(self):  # initial state
        return DataFrameColumnUsageState(self.variables)
