import itertools

from lyra.abstract_domains.state import State
from lyra.abstract_domains.usage.dataframe_usage_domain2 import DataFrameColumnUsageState
from lyra.core.expressions import Subscription, Literal, VariableIdentifier, ListDisplay, BinaryArithmeticOperation, Input, Concat
from lyra.core.statements import Call, SubscriptionAccess, SlicingAccess, VariableAccess
from lyra.core.types import (
    StringLyraType,
    ListLyraType,
    SetLyraType,
    DictLyraType,
    TupleLyraType,
    DataFrameLyraType,
)
from lyra.engine.interpreter import Interpreter
from lyra.semantics.backward import DefaultPandasBackwardSemantics


class DataFrameColumnUsageSemantics(DefaultPandasBackwardSemantics):
    """Backward semantics of statements with support for Pandas library calls for dataframe column usage analysis."""

    def _summarized_view(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        return state.output(dfs)

    def subscription_access_semantics(
            self,
            stmt: SubscriptionAccess,
            state: DataFrameColumnUsageState,
            interpreter: Interpreter,
    ) -> DataFrameColumnUsageState:
        target = self.semantics(stmt.target, state, interpreter).result
        key = self.semantics(stmt.key, state, interpreter).result
        result = set()
        for primary, index in itertools.product(target, key):
            if not isinstance(primary.typ, DataFrameLyraType):
                error = (
                    f"Semantics for subscription of {primary} is not yet implemented!"
                )
                raise NotImplementedError(error)
            if isinstance(index, ListDisplay):
                for idx in index.items:
                    subscription = Subscription(primary.typ, primary, idx)
                    result.add(subscription)
            elif isinstance(index, (Literal, VariableIdentifier)):
                subscription = Subscription(primary.typ, primary, index)
                result.add(subscription)
            else:
                error = f"Semantics for subscription of {primary} and {index} is not yet implemented!"
                raise NotImplementedError(error)

        state.result = result
        return state

    def drop_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        dataframes = self.semantics(stmt.arguments[0], state, interpreter).result
        columns = self.semantics(stmt.arguments[1], state, interpreter).result
        return state.drop_dataframe_column(dataframes, columns)

    def head_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        return self._summarized_view(stmt, state, interpreter)

    def hist_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        return self._summarized_view(stmt, state, interpreter)

    def tail_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        return self._summarized_view(stmt, state, interpreter)

    def describe_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        return self._summarized_view(stmt, state, interpreter)

    def info_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        return self._summarized_view(stmt, state, interpreter)

    def min_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        state.result = {df for df in dfs}
        return state

    def max_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        state.result = {df for df in dfs}
        return state

    def median_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        state.result = {df for df in dfs}
        return state

    def fillna_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        state.result = {df for df in dfs}
        return state

    def replace_call_semantics(self, stmt: Call, state: DataFrameColumnUsageState,
                               interpreter: Interpreter) -> DataFrameColumnUsageState:
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        state.result = {df for df in dfs}
        return state

    def concat_call_semantics(self, stmt: Call, state: DataFrameColumnUsageState,
                              interpreter: Interpreter) -> DataFrameColumnUsageState:
        # Concat always recieves a sequence (or mapping) of dfs
        lists_dfs = self.semantics(stmt.arguments[1], state, interpreter).result
        result = set()
        for l in lists_dfs:
            if not isinstance(l, ListDisplay):
                error = f"Semantics for subscription of {list} is not yet implemented!"
                raise NotImplementedError(error)

            result.add(Concat(items=l.items))
        state.result = result
        return state

    def read_csv_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        state.result = {Input(typ=StringLyraType())}
        return state
