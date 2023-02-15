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

    def _less_equal(self, other: 'Lattice') -> bool:
        return self

    def _join(self, other: 'DataFrameColumnUsageState') -> 'DataFrameColumnUsageState':
        return self

    def _meet(self, other: 'DataFrameColumnUsageState') -> 'DataFrameColumnUsageState':
        return self

    def _widening(self, other: 'DataFrameColumnUsageState') -> 'DataFrameColumnUsageState':
        return self

    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'DataFrameColumnUsageState':
        return self

    def _assign_subscription(self, left: Subscription, right: Expression) -> 'DataFrameColumnUsageState':
        return self

    def _assign_slicing(self, left: Slicing, right: Expression) -> 'DataFrameColumnUsageState':
        return self

    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'DataFrameColumnUsageState':
        return self

    def _assume_subscription(self, condition: Subscription, neg: bool = False) -> 'DataFrameColumnUsageState':
        return self

    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self

    def enter_if(self) -> 'DataFrameColumnUsageState':
        return self

    def exit_if(self) -> 'DataFrameColumnUsageState':
        return self

    def enter_loop(self) -> 'DataFrameColumnUsageState':
        return self

    def exit_loop(self) -> 'DataFrameColumnUsageState':
        return self

    def forget_variable(self, variable: VariableIdentifier) -> 'DataFrameColumnUsageState':
        return self

    def _output(self, output: Expression) -> 'DataFrameColumnUsageState':
        if isinstance(output, VariableIdentifier):
            self.store[output] = {col: UsageLattice().top() for col in self.store[output].keys()}
        return self

    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'DataFrameColumnUsageState':
        return self

    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'DataFrameColumnUsageState':
        return self

    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'DataFrameColumnUsageState':
        return self

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
