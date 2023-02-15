from lyra.abstract_domains.state import State
from lyra.abstract_domains.usage.dataframe_usage_domain import DataFrameColumnUsageState
from lyra.core.statements import Call
from lyra.engine.interpreter import Interpreter
from lyra.semantics.backward import DefaultPandasBackwardSemantics


class DataFrameColumnUsageSemantics(DefaultPandasBackwardSemantics):
    """Backward semantics of statements with support for Pandas library calls for dataframe column usage analysis."""

    def drop_call_semantics(self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter) -> DataFrameColumnUsageState:
        dataframes = self.semantics(stmt.arguments[0], state, interpreter).result
        columns = self.semantics(stmt.arguments[1], state, interpreter).result
        return state.drop_dataframe_column(dataframes, columns)

    def head_call_semantics(self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter) -> DataFrameColumnUsageState:
        dataframes = self.semantics(stmt.arguments[0], state, interpreter).result
        return state.output(dataframes)

    def read_csv_call_semantics(self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter) -> DataFrameColumnUsageState:
        return state    # TODO


