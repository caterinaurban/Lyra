from lyra.abstract_domains.state import State
from lyra.core.statements import Call
from lyra.engine.interpreter import Interpreter
from lyra.semantics.backward import DefaultPandasBackwardSemantics


class DataFrameColumnUsageSemantics(DefaultPandasBackwardSemantics):
    """Backward semantics of statements with support for Pandas library calls for dataframe column usage analysis."""

    def read_csv_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        return state    # TODO

    def drop_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        return state    # TODO
