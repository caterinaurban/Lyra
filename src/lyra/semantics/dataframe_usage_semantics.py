import itertools

from lyra.abstract_domains.state import State
from lyra.abstract_domains.usage.dataframe_usage_domain import DataFrameColumnUsageState
from lyra.core.expressions import Subscription, Literal, VariableIdentifier, ListDisplay, BinaryArithmeticOperation, Input, AttributeReference, \
        TupleDisplay
from lyra.core.dataframe_expressions import Concat, Loc, UnknownCall
from lyra.core.statements import Call, SubscriptionAccess, SlicingAccess, VariableAccess, AttributeAccess
from lyra.core.types import (
    StringLyraType,
    ListLyraType,
    SetLyraType,
    DictLyraType,
    TupleLyraType,
    DataFrameLyraType,
    AttributeAccessLyraType,
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
        # If the targets are not specifically dataframes or loc, call the
        # parent method.
        # Assumption: every element of the `target` set is of the same type,
        # and semantics call did not fail
        t = list(target)[0]
        t_attribute = isinstance(t.typ, AttributeAccessLyraType) and isinstance(t.typ.target_typ, DataFrameLyraType)
        t_dataframe = isinstance(t.typ, DataFrameLyraType)
        if not (t_attribute or t_dataframe):
            return super().subscription_access_semantics(stmt, state, interpreter)

        target = self.semantics(stmt.target, state, interpreter).result
        key = self.semantics(stmt.key, state, interpreter).result
        result = set()
        for primary, index in itertools.product(target, key):
            # FIXME maybe there should be a type for loc?? currently it is
            # string...
            if isinstance(primary, AttributeReference):
                target = primary.target
                if primary.attribute.name != "loc":
                    error = (
                        f"Semantics for subscription of attribute access {primary} is not yet implemented!"
                    )
                    raise NotImplementedError(error)
                if isinstance(index, TupleDisplay):
                    # FIXME row filtering not handled yet
                    rows = index.items[0]
                    cols = index.items[1]
                    cols_set = set()
                    if isinstance(cols, ListDisplay):
                        cols_set = set(cols.items)
                    elif isinstance(cols, (Literal, VariableIdentifier)):
                        cols_set = {cols}
                    else:
                        error = f"Semantics for loc of {primary} with columns {cols} is not yet implemented!"
                        raise NotImplementedError(error)
                    result.add(Loc(target, rows, cols=cols_set))
                else:
                    result.add(Loc(target, rows=index, cols=None)) # FIXME what happens when cols is None?
            elif isinstance(primary.typ, DataFrameLyraType):
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
            else:
                error = (
                    f"Semantics for subscription of {primary} is not yet implemented!"
                )
                raise NotImplementedError(error)

        state.result = result
        return state


    def slicing_access_semantics(self, stmt: SlicingAccess, state, interpreter) -> DataFrameColumnUsageState:
        """Semantics of a slicing access. Only for df.loc for now.

        :param stmt: slicing access statement to be executed
        :param state: state before executing the slicing access
        :return: state modified by the slicing access
        """
        target = self.semantics(stmt.target, state, interpreter).result
        # If the targets are not specifically dataframes or loc, call the
        # parent method.
        # Assumption: every element of the `target` set is of the same type,
        # and semantics call did not fail
        t = list(target)[0]
        t_attribute = isinstance(t.typ, AttributeAccessLyraType) and isinstance(t.typ.target_typ, DataFrameLyraType)
        t_dataframe = isinstance(t.typ, DataFrameLyraType)
        if not (t_attribute or t_dataframe):
            return super().slicing_access_semantics(stmt, state, interpreter)

        lower = self.semantics(stmt.lower, state, interpreter).result if stmt.lower else {None}
        upper = self.semantics(stmt.upper, state, interpreter).result if stmt.upper else {None}
        stride = self.semantics(stmt.stride, state, interpreter).result if stmt.stride else {None}
        result = set()
        for primary, start, stop, step in itertools.product(target, lower, upper, stride):
            if isinstance(primary, AttributeReference) and primary.attribute.name == "loc":
                # There is no native expression for `start:stop:step`, but what
                # is interesting in the case of `df.loc[start:stop:step]` is
                # only to know that `start`, `stop`, and `step` are mentioned.
                # Thus, a tuple `(start, stop, step)` carries the right
                # information.
                result.add(Loc(primary.target, rows=TupleDisplay(typ=None, items=[start,stop,step]), cols=None))
            else:
                raise NotImplementedError(f"Semantics of other than pd.loc ({target}) not implemented yet")
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

    def DataFrame_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        raise NotImplementedError("Semantics for pd.DataFrame not yet implemented")

    def user_defined_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        if stmt.name in interpreter.fargs:
            # If the function name is indeed user defined, then use the
            # existing function
            return super().user_defined_call_semantics(stmt, state, interpreter)
        else:
            # Otherwise, the semantics of the call is just an UnknownCall
            # expression
            ## Otherwise, the semantics of the call is just the set of columns
            ## mentioned in the arguments
            ## dfs = set()
            ## for arg in stmt.arguments:
            ##     dfs.update(self.semantics(arg, state, interpreter).result)
            ## state.result = dfs
            # FIXME works with step by step debugger, but not without??
            result = set()
            arguments = [self.semantics(arg, state, interpreter).result for arg in stmt.arguments]
            for fargs in itertools.product(*arguments):
                call = UnknownCall(typ = stmt.typ, fname = stmt.name, fargs=list(fargs))
                result.add(call)
            state.result = result
            return state
