from copy import deepcopy
from typing import Set, Union, List

from lyra.abstract_domains.lattice import BoundedLattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.usage.usage_lattice import UsageLattice
from lyra.core.expressions import Slicing, Expression, Subscription, VariableIdentifier, BinaryComparisonOperation, \
    Literal, ListDisplay

ColumnName = Union[str, None]


class DataFrameColumnUsageState(BoundedLattice, State):

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        super().__init__()                  # BoundedLattice
        State.__init__(self, precursory)    # State
        self._store = {v: {None: UsageLattice()} for v in variables}

    @property
    def store(self):
        return self._store

    def __repr__(self):
        def do(columns):
            def name(column):
                return str(column) if column else '_'
            itms = sorted(columns.items(), key=lambda x: name(x[0]))
            return "{" + ", ".join("{}: {}".format(name(column), usage) for column, usage in itms) + "}"
        items = sorted(self.store.items(), key=lambda x: x[0].name)
        return "; ".join("{} -> {}".format(variable, do(value)) for variable, value in items)

    def _less_equal(self, other: 'DataFrameColumnUsageState') -> bool:
        raise NotImplementedError('_less_equal in DataFrameColumnUsageState is not yet implemented!')

    def _join(self, other: 'DataFrameColumnUsageState') -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_join in DataFrameColumnUsageState is not yet implemented!')

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
        return self

    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'DataFrameColumnUsageState':
        used = any(usage.is_top() for usage in self.store[left].values())
        scoped = any(usage.is_scoped() for usage in self.store[left].values())
        if used or scoped:
            # the assigned variable is used or scoped
            self.store[left] = {None: UsageLattice().written()}
        return self

    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_substitute_subscription in DataFrameColumnUsageState is not yet implemented!')

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
