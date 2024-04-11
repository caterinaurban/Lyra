from collections import defaultdict
from copy import deepcopy
from typing import Set, Union

from lyra.abstract_domains.lattice import BoundedLattice
from lyra.core.expressions import walk, Input
from lyra.abstract_domains.state import State
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.usage.usage_lattice import UsageLattice
from lyra.abstract_domains.usage.usage_domain import UsageStore
from lyra.core.expressions import Slicing, Expression, Subscription, \
    VariableIdentifier, BinaryComparisonOperation, Literal, ListDisplay
from lyra.core.types import LyraType, DataFrameLyraType
from lyra.core.utils import copy_docstring

ColumnName = Union[str, None]

class DataFrameColumnType(LyraType):
    """Dummy type for names of columns of dataframes.
    No Python expression shall actually have this type."""

    def __repr__(self):
        return "DataFrameColumn"

class DataFrameColumnIdentifier(VariableIdentifier):
    """Fake "variable" identifier for the sole purpose of embedding column
    names into VariableIdentifier and to reuse Store."""

    def __init__(self, name: ColumnName):
        """Dataframe column identifier construction.

        :param name: name of the column identifier, a string or None (that
                     represents any column)
        """

        # TODO find out what "special" does and see if it applies here
        super().__init__(typ=DataFrameColumnType, name=name)

    def __str__(self):
        return "_" if self.name is None else super().__str__(self)

class DataFrameColumnUsageLattice(UsageStore):
    """A store mapping each column of a dataframe to its usage status.

    There is a special column _ to represent all other (unnamed) columns.
    """

    def __init__(self):
        """Construct default lattice element.
        The default store is {_ -> N}

        :param columns: set of columns of the dataframe"""
        variables = {DataFrameColumnIdentifier(name=None)}
        lattices = {DataFrameColumnType: UsageLattice}
        super().__init__(variables, lattices)

    # FIXME methods such as add_variable must create DataFrameColumnIdentifiers

    def __repr__(self):
        return "{" + super().__repr__() + "}"

# TODO rename? this is not only about DataFrames
class DataFrameColumnUsageState(Stack, State):
    """Input data usage analysis state for both dataframes and normal
    variables.

    TODO add stack
    """

    def __init__(self, variables, precursory: State = None):
        # all variables are abstracted in the basic usage lattice...
        lattices = defaultdict(lambda: UsageLattice)

        # ...except pandas dataframes which are abstracted by their own lattice
        lattices[DataFrameLyraType(library="pd")] = DataFrameColumnUsageLattice
        # TODO make this library-independent

        # init Stack
        super().__init__(UsageStore,
                         {'variables': variables, 'lattices': lattices})
        State.__init__(self, precursory) # State

    # push and pop functions copied from SimpleUsageState
    # TODO check that they are right
    @copy_docstring(Stack.push)
    def push(self):
        if self.is_bottom() or self.is_top():
            return self
        self.stack.append(deepcopy(self.lattice).increase())
        return self

    @copy_docstring(Stack.pop)
    def pop(self):
        if self.is_bottom() or self.is_top():
            return self
        current = self.stack.pop()
        self.lattice.decrease(current)
        return self

    def _assign_any(self, left: Expression, right: Expression):
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'SimpleUsageState':
        return self._assign_any(left, right)

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'SimpleUsageState':
        return self._assign_any(left, right)

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'SimpleUsageState':
        return self._assign_any(left, right)

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
        raise NotImplementedError('_output in DataFrameColumnUsageState is not yet implemented!')

    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_substitute_variable in DataFrameColumnUsageState is not yet implemented!')

    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_substitute_subscription in DataFrameColumnUsageState is not yet implemented!')

    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_substitute_slicing in DataFrameColumnUsageState is not yet implemented!')

