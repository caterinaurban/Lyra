import itertools
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
        VariableIdentifier, BinaryComparisonOperation, Literal, ListDisplay, \
        Concat
from lyra.core.types import LyraType, DataFrameLyraType, StringLyraType
from lyra.core.utils import copy_docstring

ColumnName = Union[str, None]

def is_used(x):
    return x.is_top() or x.is_scoped()

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

        if isinstance(name, str) or name is None:
            super().__init__(typ=DataFrameColumnType, name=name)
        elif isinstance(name, Literal) and name.typ == StringLyraType():
            super().__init__(typ=DataFrameColumnType, name=name.val)
        elif isinstance(name, DataFrameColumnIdentifier):
            return
        else:
            raise ValueError("Cannot create DataFrameColumnIdentifier out of "
                             f"{name} of type {type(name)}")

    # used when sorting column names
    def __lt__(self, other):
        return other.name is None or str(self) < str(other)

    def __str__(self):
        return "_" if self.name is None else super().__str__()

def _get_columns(df: VariableIdentifier, expr: Expression) -> Set['DataFrameColumnIdentifier']:
    """Return the set of the columns of [df] present in [expr]"""
    columns = set()

    for e in walk(expr):
        if isinstance(e, Subscription) and isinstance(e.typ, DataFrameLyraType):
            if not e.target == df:
                continue
            try:
                columns.add(DataFrameColumnIdentifier(e.key))
            except ValueError:
                # if the column name cannot be transformed into a column
                # identifier, then act as if there were no columns so the next
                # action applies to the wole dataframe
                return None

    return columns


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
        items = sorted(self.store.items())
        return "{" \
                + ", ".join("{} -> {}".format(variable, value) for variable, value in items) \
                + "}"

    def _get_default(self):
        default_col = DataFrameColumnIdentifier(None)
        if default_col in self.store:
            return self.store[default_col]
        else:
            raise Exception(f"DataFrameColumnUsageLattice._get_default {self} did not have a default column!")

    def get(self, col: DataFrameColumnIdentifier):
        if col in self.store:
            return self.store[col]
        else:
            return self._get_default()

    def _top_whole_dataframe(self):
        """Make the whole dataframe used.
        This loses the column information.
        """
        self.__init__()
        self._get_default().top()
        return self

    def top(self, columns=None):
        """Use some columns of a dataframe.

        If no column is provided, then the whole dataframe is used.

        :param columns: Set of columns to mark used.
        """
        if not columns:
            self._top_whole_dataframe()
            return self
        else:
            for col in columns:
                if col not in self.variables:
                    self.add_variable(col)
                self.store[col].top()
        return self

    def is_any_top(self):
        return any(element.is_top() for element in self.store.values())

    def _written_whole_dataframe(self):
        """Overwrite a whole dataframe.
        This loses the column information.
        """
        self.__init__()
        self._get_default().written()
        return self

    def written(self, columns=None):
        """Overwrite some columns of a dataframe.

        If no column is provided, then the whole dataframe is overwritten.

        :param columns: Set of columns to overwrite.
        """
        if not columns:
            self._written_whole_dataframe()
            return self
        else:
            for col in columns:
                if col not in self.variables:
                    self.add_variable(col)
                self.store[col].written()
        return self

    def is_scoped(self):
        """The current dataframe is scoped if all of its columns are scoped"""
        return all(element.is_scoped() for element in self.store.values())

    def is_any_scoped(self):
        return any(element.is_scoped() for element in self.store.values())

    def _bottom_whole_dataframe(self):
        """Make whole dataframe unused (resets it).
        This loses the column information.
        """
        self.__init__()
        return self

    def bottom(self, columns=None):
        """Make some columns of a dataframe unused.

        If no column is provided, then the whole dataframe is unused.

        :param columns: Set of columns to mark unused.
        """
        if not columns:
            self._bottom_whole_dataframe()
            return self
        else:
            for col in columns:
                if col not in self.variables:
                    self.add_variable(col)
                self.store[col].bottom()
        return self

    def is_bottom(self):
        """A dataframe is bottom if and only if it is {_ -> N}.
        For instance, {"A" -> N, _ -> N} is NOT bottom.

        This is coherent with self.bottom() returning {_ -> N}.
        """
        if len(self.store) == 0:
            raise Exception(f"DataFrameColumnUsageLattice.is_bottom {self} did not have a default column!")
        return len(self.store) == 1 and self._get_default().is_bottom()

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

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'DataFrameColumnUsageState':
        # TODO factorize with code from _substitute_variable
        # TODO this takes time O(|output| * |output.ids()|), make it O(|output|)
        for identifier in output.ids():
            if isinstance(identifier.typ, DataFrameLyraType):
                columns = _get_columns(identifier, output)
                if columns:
                    # If columns are mentioned explicitly, then mark them as
                    # used
                    self.lattice.store[identifier].top(columns)
                else:
                    # If no columns are mentioned explicitly, then mark all
                    # columns that are not overwritten as used to keep column
                    # name information, and lose information about overwritten
                    # columns.
                    # TODO make this handle head(df["A"] + df) properly
                    columns_not_written = {col for col, elt in self.lattice.store[identifier].store.items() if not elt.is_written()}
                    self.lattice.store[identifier].top(columns_not_written)
                    columns_written = {col for col, elt in self.lattice.store[identifier].store.items() if elt.is_written()}
                    for col in columns_written:
                        self.lattice.store[identifier].remove_variable(col)
            else:
                self.lattice.store[identifier].top()
        return self

    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'DataFrameColumnUsageState':
        # expression of the form x = e
        # For now, change the state if one of the columns of the assigned dataframe is U or S
        # DONE make this finer by propagating used columns up to the columns of
        # the rhs
        if self.lattice.store[left].is_any_top() or self.lattice.store[left].is_any_scoped():
            old_left_store = deepcopy(self.lattice.store[left])
            self.lattice.store[left].written()
            # if left.is_dictionary:
            #     self.lattice.keys[left.keys].written()
            #     self.lattice.values[left.values].written()
            if isinstance(right, Concat):
                # concatenation loses column information and marks every rhs
                # column used if lhs has one
                for identifier in right.ids():
                    self.lattice.store[identifier].top()
                return self
            for identifier in right.ids():
                if isinstance(identifier.typ, DataFrameLyraType):
                    # columns = _get_columns(identifier, right)
                    self.lattice.store[identifier].unify(old_left_store) # copy columns from lhs
                    columns = _get_columns(identifier, right) or self.lattice.store[identifier].variables
                    # filter for only the columns that are used on the lhs, to
                    # "transfer" usage
                    used_columns = {col for col in columns if is_used(old_left_store.get(col))}
                    unused_columns = columns.difference(used_columns)
                    if used_columns:
                        self.lattice.store[identifier].top(used_columns)
                    if unused_columns:
                        self.lattice.store[identifier].bottom(unused_columns)
                else:
                    self.lattice.store[identifier].top()
                # if identifier.is_dictionary:
                #     self.lattice.keys[identifier.keys].top()
                #     self.lattice.values[identifier.values].top()
        return self

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'DataFrameColumnUsageState':
        # expression of the form df["a"] = e
        target = left.target
        try:
            key = DataFrameColumnIdentifier(left.key)
        except ValueError:
            # If the key cannot be coerced to a column name
            if self.lattice.store[target].is_any_scoped():
                # TODO figure out what to do here, perhaps mark everything as used? or scoped?
                raise NotImplementedError("Handling of substitute_subscription with unknown scoped column is not implemented")
            elif self.lattice.store[target].is_any_top():
                # If at least one column is used, we don't know if this column
                # is overwritten or stays used, and what happens to other
                # columns. To overapproximate: mark all columns as used.
                self.lattice.store[target]._top_whole_dataframe()
        else:
            # If the key is a valid column name
            # only change the state if the assigned column is U or S
            if is_used(self.lattice.store[target].get(key)):
                self.lattice.store[target].written({key})
                # use rhs identifiers
                for identifier in right.ids():
                    if isinstance(identifier.typ, DataFrameLyraType):
                        columns = _get_columns(identifier, right)
                        if columns:
                            # contrary to what happens in
                            # `_substitute_variable`, here we know that the
                            # column on the lhs is used, so the "transfer" is
                            # done by marking the rhs columns involved as top
                            self.lattice.store[identifier].top(columns)
                        else:
                            # TODO make this guard also catch df["A"] + df
                            raise Exception("Expected dataframe on right hand side of subscription substitution to be subscripted, but no column name was found.")
                    else:
                        self.lattice.store[identifier].top()
        return self

    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_substitute_slicing in DataFrameColumnUsageState is not yet implemented!')

    def _drop_dataframe_column(self, dataframe: Expression, columns: Set[Expression]):
        # TODO maybe some of this logic should be handled by the semantics, and not here
        if isinstance(dataframe, VariableIdentifier):
            # If any column cannot be made into a DataFrameColumnIdentifier,
            # then mark the whole dataframe as unused
            try:
                cols_to_unuse : Set[DataFrameColumnIdentifier] = set()
                for col in columns:
                    if isinstance(col, ListDisplay):
                        for c in col.items:
                            cols_to_unuse.add(DataFrameColumnIdentifier(c))
                    else:
                        cols_to_unuse.add(DataFrameColumnIdentifier(col))
            except ValueError:
                columns = None
            self.lattice.store[dataframe].bottom(cols_to_unuse)
            return self
        raise ValueError(f"Unexpected dropping of columns to {dataframe}!")

    def drop_dataframe_column(self, dataframes: Set[Expression], columns: Set[Expression]):
        if self.is_bottom():
            return self
        self.big_join([deepcopy(self)._drop_dataframe_column(df, columns) for df in dataframes])
        self.result = set()
        return self

