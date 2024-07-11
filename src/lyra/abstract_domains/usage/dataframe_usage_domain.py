import itertools
from collections import defaultdict
from copy import deepcopy
from typing import Set, Union
from enum import Enum

from lyra.abstract_domains.lattice import BoundedLattice, EnvironmentMixin
from lyra.core.expressions import walk, Input
from lyra.abstract_domains.state import State
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.usage.usage_lattice import UsageLattice
from lyra.abstract_domains.usage.usage_domain import UsageStore
from lyra.core.expressions import Slicing, Expression, Subscription, \
        VariableIdentifier, BinaryComparisonOperation, Literal, ListDisplay, \
        AttributeReference
from lyra.core.dataframe_expressions import Concat, Loc
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

class DataFrameColumnKind(Enum):
    NAMED = 0
    INDEX = 1
    DEFAULT = 2

    def __lt__(self, other: 'DataFrameColumnKind'):
        return self.value < other.value

class DataFrameColumnIdentifier(VariableIdentifier):
    """Fake "variable" identifier for the sole purpose of embedding column
    names into VariableIdentifier and to reuse Store."""

    def __init__(self, name: ColumnName, kind: DataFrameColumnKind = None):
        """Dataframe column identifier construction.

        For backwards compatibility, if no kind is given, then the column
        identifier will be DEFAULT if no name is given, and NAMED otherwise.

        :param name: name of the column identifier, a string or None (for DEFAULT and INDEX kinds)
        :param kind: kind of the column identifier, DEFAULT, INDEX, or NAMED
        """

        if name is None and kind is None:
            self._kind = DataFrameColumnKind.DEFAULT
        elif kind is None:
            self._kind = DataFrameColumnKind.NAMED
        else:
            self._kind = kind

        if self.kind == DataFrameColumnKind.DEFAULT:
            super().__init__(typ=DataFrameColumnType, name="!default")
        elif self.kind == DataFrameColumnKind.INDEX:
            super().__init__(typ=DataFrameColumnType, name="!index")
        else: # NAMED
            if isinstance(name, str):
                super().__init__(typ=DataFrameColumnType, name=name)
            elif isinstance(name, Literal) and name.typ == StringLyraType():
                super().__init__(typ=DataFrameColumnType, name=name.val)
            elif isinstance(name, DataFrameColumnIdentifier):
                return
            else:
                raise ValueError("Cannot create DataFrameColumnIdentifier out of "
                                 f"{name} of type {type(name)}")

    @property
    def kind(self):
        return self._kind

    # used when sorting column names
    def __lt__(self, other):
        return self.kind < other.kind or self.name < other.name

    def __str__(self):
        if self.kind == DataFrameColumnKind.DEFAULT:
            return "_"
        elif self.kind == DataFrameColumnKind.INDEX:
            return "(index)"
        elif self.kind == DataFrameColumnKind.NAMED:
            return super().__str__()

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
        if isinstance(e, Loc) and e.typ is DataFrameLyraType: # FIXME I don't understand why Loc is DataFrameLyraType and not an instance?
            if not e.target == df:
                continue
            if not e.columns:
                # if somewhere in expr a loc is applied without a column
                # filter, then it supersedes all columns already found
                return None
            else:
                # otherwise append all mentioned columns
                try:
                    columns.update({DataFrameColumnIdentifier(col) for col in e.columns})
                except ValueError:
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

    def is_written(self):
        """The current dataframe is written if all of its columns are written"""
        return all(element.is_written() for element in self.store.values())

    def is_any_written(self):
        return any(element.is_written() for element in self.store.values())

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

    def decrease(self, other: 'DataFrameColumnUsageLattice') -> 'DataFrameColumnUsageLattice':
        # TODO docstring
        self.unify(other)

        for var in self.store:
            self.get(var).decrease(other.get(var))
        return self

# TODO rename? this is not only about DataFrames
class DataFrameColumnUsageState(Stack, State, EnvironmentMixin):
    """Input data usage analysis state for both dataframes and normal
    variables.

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

    # TODO add_variable, remove_variable, unify -> call the ones from the lattice

    @copy_docstring(EnvironmentMixin.add_variable)
    def add_variable(self, variable: VariableIdentifier):
        self.lattice.add_variable(variable)
        return self

    @copy_docstring(EnvironmentMixin.remove_variable)
    def remove_variable(self, variable: VariableIdentifier):
        self.lattice.remove_variable(variable)
        return self

    @copy_docstring(EnvironmentMixin.unify)
    def unify(self, other: 'DataFrameColumnsUsageState'):
        self.lattice.unify(other.lattice)
        return self


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

    def _assume_any(self, condition: Expression) -> 'SimpleUsageState':
        effect = False  # effect of the current nesting level on the outcome of the program
        for variable in self.lattice.variables:
            value = self.lattice.store[variable]
            if isinstance(value, DataFrameColumnUsageLattice):
                if value.is_any_written() or value.is_any_top():
                    effect = True
                    break
            else:
                if value.is_written() or value.is_top():
                    effect = True
                    break
        if effect:  # the current nesting level has an effect on the outcome of the program
            self._output(condition)
            # for identifier in condition.ids():
            #     self.lattice.store[identifier].top()
            #     if identifier.is_dictionary:
            #         self.lattice.keys[identifier.keys].top()
            #         self.lattice.values[identifier.values].top()
        return self

    @copy_docstring(State._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_subscription)
    def _assume_subscription(self, condition: Subscription, neg: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_noteq_comparison)
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_lt_comparison)
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_lte_comparison)
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_gt_comparison)
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_gte_comparison)
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_is_comparison)
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    @copy_docstring(State._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'SimpleUsageState':
        return self._assume_any(condition)

    def enter_if(self) -> 'DataFrameColumnUsageState':
        return self.push()

    def exit_if(self) -> 'DataFrameColumnUsageState':
        return self.pop()

    def enter_loop(self) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('enter_loop in DataFrameColumnUsageState is not yet implemented!')

    def exit_loop(self) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('exit_loop in DataFrameColumnUsageState is not yet implemented!')

    @copy_docstring(State.forget_variable)
    def forget_variable(self, variable: VariableIdentifier) -> 'DataFrameColumnUsageState':
        super().forget_variable(variable)
        return self

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

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'State':
        """Substitute an expression to another expression.
        Extends State._substitute"""

        if isinstance(left, Loc):
            return self._substitute_loc(left, right)
        elif isinstance(left, AttributeReference):
            if isinstance(left.target.typ, DataFrameLyraType) and left.attribute.name == "index":
                # `df.index = ...` does nothing
                return self
            else:
                raise Exception(f"unknown attribute for dataframe: {left.attribute}")
        else:
            return super()._substitute(left,right)

    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'DataFrameColumnUsageState':
        # expression of the form x = e
        # For now, change the state if one of the columns of the assigned dataframe is U or S
        # DONE make this finer by propagating used columns up to the columns of
        # the rhs
        if isinstance(self.lattice.store[left], DataFrameColumnUsageLattice):
            is_top_or_scoped = self.lattice.store[left].is_any_top() or self.lattice.store[left].is_any_scoped()
        else:
            is_top_or_scoped = self.lattice.store[left].is_top() or self.lattice.store[left].is_scoped()
        if is_top_or_scoped:
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
                    # self.lattice.store[identifier].unify(old_left_store) # copy columns from lhs
                    columns = _get_columns(identifier, right) or self.lattice.store[identifier].variables
                    # filter for only the columns that are used on the lhs, to
                    # "transfer" usage
                    used_columns = {col for col in columns if is_used(old_left_store.get(col))}
                    if used_columns:
                        self.lattice.store[identifier].top(used_columns)
                    written_columns = {col for col in columns if old_left_store.get(col).is_written()}
                    if written_columns:
                        self.lattice.store[identifier].written(written_columns)
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
                            # NOTE REU: actually it is ok if some dataframes
                            # don't have columns mentioned (and it is
                            # independent from their begin call arguments):
                            # this should be a typing issue...
                            self.lattice.store[identifier].top()
                            # raise Exception("Expected dataframe on right hand side of subscription substitution, but no column name was found.")
                    else:
                        self.lattice.store[identifier].top()
        return self

    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'DataFrameColumnUsageState':
        raise NotImplementedError('_substitute_slicing in DataFrameColumnUsageState is not yet implemented!')

    def _substitute_loc(self, left: Loc, right: Expression) -> 'DataFrameColumnUsageState':
        self.push()
        substs = set()
        if left.columns:
            for col in left.columns:
                substs.add(Subscription(typ=left.typ, target=left.target, key=col))
        else:
            # if no columns are specified, then the substitution will be for the whole target
            substs = {left.target}
        self.substitute(left=substs, right={right})
        self.assume({left.rows}, bwd=True)
        self.pop()
        return self
    # raise NotImplementedError('_substitute_loc in DataFrameColumnUsageState is not yet implemented!')


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

            for col in cols_to_unuse:
                if col in self.lattice.store[dataframe].store and is_used(self.lattice.store[dataframe].store[col]):
                    print(f"Warning: column {col} of {dataframe} dropped before use!") # TODO add line information?

            self.lattice.store[dataframe].bottom(cols_to_unuse)
            return self
        raise ValueError(f"Unexpected dropping of columns to {dataframe}!")

    def drop_dataframe_column(self, dataframes: Set[Expression], columns: Set[Expression]):
        if self.is_bottom():
            return self
        self.big_join([deepcopy(self)._drop_dataframe_column(df, columns) for df in dataframes])
        self.result = set()
        return self

