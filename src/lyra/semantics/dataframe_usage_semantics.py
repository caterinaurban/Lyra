import itertools

from lyra.abstract_domains.state import State
from lyra.abstract_domains.usage.dataframe_usage_domain import DataFrameColumnUsageState, DataFrameColumnIdentifier, DataFrameColumnKind
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
        """Common semantics for all calls that simply use whole columns or dataframes.
        This function assumes the call takes exactly one argument, that may be
        a container (eg. df[["A","B"]].head())
        See head_call_semantics for instance.
        """
        dfs = self.semantics(stmt.arguments[0], state, interpreter).result
        return state.output(dfs)

    def subscription_access_semantics(
            self,
            stmt: SubscriptionAccess,
            state: DataFrameColumnUsageState,
            interpreter: Interpreter,
    ) -> DataFrameColumnUsageState:
        target = self.semantics(stmt.target, state, interpreter).result
        # If the targets are not specifically dataframes or loc, fall back to
        # the generic semantics
        # Assumption: every element of the `target` set is of the same type,
        # and semantics call did not fail
        t = list(target)[0]
        t_attribute = isinstance(t.typ, AttributeAccessLyraType) and isinstance(t.typ.target_typ, DataFrameLyraType)
        t_dataframe = isinstance(t.typ, DataFrameLyraType)
        if not (t_attribute or t_dataframe):
            return super().subscription_access_semantics(stmt, state, interpreter)

        # Otherwise, the subscription can be a df.loc or simply the subsription
        # of a dataframe

        target = self.semantics(stmt.target, state, interpreter).result
        key = self.semantics(stmt.key, state, interpreter).result
        result = set()
        for primary, index in itertools.product(target, key):
            if isinstance(primary, AttributeReference):
                target = primary.target
                if primary.attribute.name != "loc":
                    error = (
                        f"Semantics for subscription of attribute access {primary} is not yet implemented!"
                    )
                    raise NotImplementedError(error)
                # If the subscription is a loc, then create a Loc expression.
                # The filter on the rows is kept as-is, because we are only
                # interested in walking that expression to see which variables
                # (or df columns) it uses.
                if isinstance(index, TupleDisplay):
                    # df.loc[rows, cols]
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
                    # df.loc[rows]
                    result.add(Loc(target, rows=index, cols=None))
            elif isinstance(primary.typ, DataFrameLyraType):
                # If the subscription is a simple dataframe subscription, the
                # semantics is just a Subscription expression
                if isinstance(index, (Literal, VariableIdentifier, ListDisplay)):
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
        """Semantics of a slicing access. For now only for df.loc with no column filter

        :param stmt: slicing access statement to be executed
        :param state: state before executing the slicing access
        :return: state modified by the slicing access
        """
        target = self.semantics(stmt.target, state, interpreter).result
        # If the targets are not specifically dataframes or loc, fall back to
        # the generic semantics
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

    def attribute_access_semantics(self, stmt: AttributeAccess, state, interpreter) -> State:
        # Note that df.loc is not handled here because the full expression is
        # actually a subscription (or a slice) whose target is an
        # AttributeAccess.
        # On the other hand, df.index is simply an AttributeAccess.
        target = self.semantics(stmt.target, state, interpreter).result
        is_target_dataframe = any(isinstance(t.typ, DataFrameLyraType) for t in target)
        if is_target_dataframe and stmt.attr.name == "index":
            # The semantics for df.index is df[(index)] where "(index)" is a
            # special dataframe column. See DataFrameColumnIdentifier.
            result = set()
            index = DataFrameColumnIdentifier(name=None, kind=DataFrameColumnKind.INDEX)
            for t in target:
                subscription = Subscription(t.typ, t, index)
                result.add(subscription)
            state.result = result
            return state
        else:
            # If the attribute is not specific to dataframes, fall back to the
            # generic semantics.
            return super().attribute_access_semantics(stmt, state, interpreter)

    def drop_call_semantics(
            self, stmt: Call, state: DataFrameColumnUsageState, interpreter: Interpreter
    ) -> DataFrameColumnUsageState:
        dataframes = self.semantics(stmt.arguments[0], state, interpreter).result
        columns = self.semantics(stmt.arguments[1], state, interpreter).result
        return state.drop_dataframe_column(dataframes, columns, pp=stmt.pp)

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
        # Assumption: the argument of the concat call is always a sequence (or mapping) of dataframes
        # The semantics is simply to build a Concat expression that will be handled later
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
            # expression, that will contain the arguments.
            result = set()
            arguments = [self.semantics(arg, state, interpreter).result for arg in stmt.arguments]
            for fargs in itertools.product(*arguments):
                call = UnknownCall(typ = stmt.typ, fname = stmt.name, fargs=list(fargs))
                result.add(call)
            state.result = result
            return state
