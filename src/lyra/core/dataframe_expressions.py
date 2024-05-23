"""
Dataframe Expressions
"""

from typing import List

from lyra.core.expressions import Expression


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

    def __eq__(self, other: 'ConcatExpression'):
        return self.items == other.items

    def __hash__(self):
        return hash(str(self.items))

    def __str__(self):
        items = map(str, self.items)
        return "Concat(" + ", ".join(items) + ")"

