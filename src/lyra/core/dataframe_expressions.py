"""
Dataframe Expressions
"""

from typing import List, Set

from lyra.core.expressions import Expression
from lyra.core.types import DataFrameLyraType

# class DataFrameExpressionVisitor(metaclass=ABCMeta):


class Concat(Expression):
    """Dataframe concat expression.
    """

    def __init__(self, items: List[Expression] = None):
        """Dataframe concat construction.

        :param items: set of items being concatenated
        """
        self._items = items or []

    @property
    def items(self):
        return self._items

    def __eq__(self, other: 'Concat'):
        return self.items == other.items

    def __hash__(self):
        return hash(str(self.items))

    def __str__(self):
        items = map(str, self.items)
        return "Concat(" + ", ".join(items) + ")"

class Loc(Expression):
    """Dataframe loc expression.
    see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.loc.html
    """

    def __init__(self, target: Expression, rows: Expression, cols: Set[Expression] = None):
        """Dataframe loc construction.
        For target.loc[rows, cols]

        :param target: dataframe on which the loc is applied
        :param rows: filter applied on the rows
        :param cols: selected columns. Can be empty
        """
        self._target = target
        self._rows = rows
        self._cols = cols or set()
        self._typ = DataFrameLyraType
        pass

    @property
    def target(self):
        return self._target

    @property
    def rows(self):
        return self._rows

    @property
    def columns(self):
        return self._cols

    def __eq__(self, other: 'Loc'):
        return self.target == other.target and \
                self.rows == other.rows and \
                self.columns == other.columns

    def __hash__(self):
        return hash(str(self.target)+str(self.rows)+str(self.columns))

    def __str__(self):
        return "{}.loc[{}, {}]".format(str(self.target), str(self.rows), str(self.columns))
