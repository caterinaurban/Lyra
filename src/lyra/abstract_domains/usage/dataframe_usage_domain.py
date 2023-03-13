from copy import deepcopy
from typing import Set, Union, Dict

from lyra.abstract_domains.lattice import BoundedLattice
from lyra.core.expressions import walk
from lyra.abstract_domains.state import State
from lyra.abstract_domains.usage.usage_lattice import UsageLattice
from lyra.core.expressions import Slicing, Expression, Subscription, VariableIdentifier, BinaryComparisonOperation, \
    Literal, ListDisplay
from lyra.core.types import DataFrameLyraType

ColumnName = Union[str, None]


def _get_columns(df: VariableIdentifier, expr: Expression):
    columns = set()

    for e in walk(expr):
        if isinstance(e, Subscription) and isinstance(e.typ, DataFrameLyraType):
            if not e.target == df:
                continue
            columns.add(e.key)

    return columns


class DataFrameColumnUsageState(BoundedLattice, State):

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        super().__init__()  # BoundedLattice
        State.__init__(self, precursory)  # State
        self._store = {v: {None: UsageLattice()} for v in variables}

    @property
    def store(self):
        return self._store

    def __repr__(self):
        def do(columns):
            def name(column):
                return str(column) if column else '_'

            _items = sorted(columns.items(), key=lambda x: name(x[0]))
            return "{" + ", ".join("{}: {}".format(name(column), usage) for column, usage in _items) + "}"

        items = sorted(self.store.items(), key=lambda x: x[0].name)
        return "; ".join("{} -> {}".format(variable, do(value)) for variable, value in items)

    def _less_equal(self, other: 'DataFrameColumnUsageState') -> bool:
        raise NotImplementedError('_less_equal in DataFrameColumnUsageState is not yet implemented!')

    @staticmethod
    def _merge_var_stores(s1: Dict[ColumnName, UsageLattice], s2: Dict[ColumnName, UsageLattice]) -> dict:
        result = {}
        for column in s1:
            if s2.get(column) is None:
                result[column] = s1[column]
                continue

            lat1 = s1[column]
            lat2 = s2[column]
            result[column] = lat1.join(lat2)

        result.update({key: value for key, value in s2.items() if key not in s1.keys()})
        return result

    def _join(self, other: 'DataFrameColumnUsageState') -> 'DataFrameColumnUsageState':
        for var in other.store:
            usage = self.store.get(var, None)
            if not usage:
                self.store[var] = other.store[var]
                continue
            self.store[var] = self._merge_var_stores(self.store[var], other.store[var])

        return self

    def _meet(self, other: 'DataFrameColumnUsageState') -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_meet in DataFrameColumnUsageState is not yet implemented!')

    def _widening(self, other: 'DataFrameColumnUsageState') -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_widening in DataFrameColumnUsageState is not yet implemented!')

    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_assign_variable in DataFrameColumnUsageState is not yet implemented!')

    def _assign_subscription(self, left: Subscription, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_assign_subscription in DataFrameColumnUsageState is not yet implemented!')

    def _assign_slicing(self, left: Slicing, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_assign_slicing in DataFrameColumnUsageState is not yet implemented!')

    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_assume_variable in DataFrameColumnUsageState is not yet implemented!')

    def _assume_subscription(self, condition: Subscription, neg: bool = False) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_assume_subscription in DataFrameColumnUsageState is not yet implemented!')

    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_eq_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_noteq_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_lt_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_lte_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_gt_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_gte_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_is_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_isnot_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_in_comparison in DataFrameColumnUsageState is not yet implemented!')

    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        raise NotImplementedError('_assume_notin_comparison in DataFrameColumnUsageState is not yet implemented!')

    def enter_if(self) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('enter_if in DataFrameColumnUsageState is not yet implemented!')

    def exit_if(self) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('exit_if in DataFrameColumnUsageState is not yet implemented!')

    def enter_loop(self) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('enter_loop in DataFrameColumnUsageState is not yet implemented!')

    def exit_loop(self) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('exit_loop in DataFrameColumnUsageState is not yet implemented!')

    def forget_variable(self, variable: VariableIdentifier) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('forget_variable in DataFrameColumnUsageState is not yet implemented!')

    def _output(self, output: Expression) -> 'DataFrameColumnUsageState':
        if isinstance(output, VariableIdentifier):
            self.store[output] = {col: UsageLattice().top() for col in self.store[output].keys()}
        elif isinstance(output, Subscription):
            analysis = self.store.get(output.target, {None: UsageLattice()})
            analysis[output.key] = UsageLattice().top()
            self.store[output.target] = analysis
        return self

    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'DataFrameColumnUsageState':
        # Ignore variable if the substitution is not a DataFrame
        if not isinstance(right.typ, DataFrameLyraType):
            return self

        # Clean it up variable if right is not a subscription
        if not isinstance(right, Subscription):
            self.store[left] = {None: UsageLattice()}
            return self

        for idn in right.ids():
            # new variable `left` has the information of the columns in `idn`
            # self.store[left][right.key] = UsageLattice()

            if right.key in self.store[idn].keys():
                continue

            # We know now that columns in the identifier exists, so we add the information to the store
            self.store[idn][right.key] = self.store[idn][None]

        return self

    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'DataFrameColumnUsageState':
        if left.key in self.store[left.target]:
            self.store[left.target][left.key] = UsageLattice().written()

        for _id in right.ids():
            if not isinstance(_id.typ, DataFrameLyraType):
                continue

            columns = _get_columns(_id, right)
            self.store[_id].update({column: UsageLattice().top() for column in columns})

        return self

    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_substitute_slicing in DataFrameColumnUsageState is not yet implemented!')

    def _drop_dataframe_column(self, dataframe: Expression, columns: Expression):
        if isinstance(dataframe, VariableIdentifier):
            if isinstance(columns, Literal):
                self.store[dataframe][columns] = UsageLattice()
            elif isinstance(columns, ListDisplay):
                for col in columns.items:
                    if isinstance(col, Literal):
                        self.store[dataframe][col] = UsageLattice()
            return self
        raise ValueError(f"Unexpected dropping of columns to {dataframe}!")

    def drop_dataframe_column(self, dataframes: Set[Expression], columns: Set[Expression]):
        if self.is_bottom():
            return self
        self.big_join([deepcopy(self)._drop_dataframe_column(df, cols) for df in dataframes for cols in columns])
        self.result = set()
        return self
