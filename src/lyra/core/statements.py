"""
Statements
==========

Lyra's internal representation of Python statements.

:Authors: Caterina Urban and Simon Wehrli
"""

from abc import ABCMeta, abstractmethod
from typing import List

from lyra.core.expressions import Expression, VariableIdentifier, AttributeIdentifier
from lyra.core.types import LyraType


class ProgramPoint:
    def __init__(self, line: int, column: int):
        """Program point representation.

        :param line: line of the program
        :param column: column of the program
        """
        self._line = line
        self._column = column

    @property
    def line(self):
        return self._line

    @property
    def column(self):
        return self._column

    def __eq__(self, other: 'ProgramPoint'):
        return (self.line, self.column) == (other.line, other.column)

    def __hash__(self):
        return hash((self.line, self.column))

    def __ne__(self, other: 'ProgramPoint'):
        return not (self == other)

    def __repr__(self):
        """Unambiguous string representation of the program point

        :return: unambiguous string representation
        """
        return "[line:{0.line}, column:{0.column}]".format(self)


class Statement(metaclass=ABCMeta):
    """Statement representation.

    https://docs.python.org/3.4/reference/simple_stmts.html
    """

    def __init__(self, pp: ProgramPoint):
        """Statement construction.

        :param pp: program point associated with the statement
        """
        self._pp = pp

    @property
    def pp(self):
        return self._pp

    @abstractmethod
    def __repr__(self):
        """Unambiguous string representation of the statement.

        :return: string representing the statement
        """


class LibraryAccess(Statement):
    """Library access representation."""

    def __init__(self, pp, library: str, name: str):
        super().__init__(pp)
        self._library = library
        self._name = name

    @property
    def library(self):
        return self._library

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return "{0.library}".format(self)


"""
Expression Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#expression-statements
"""


class LiteralEvaluation(Statement):
    """Literal evaluation representation."""

    def __init__(self, pp, literal: Expression):
        """Literal evaluation construction.

        :param pp: program point associated with the literal evaluation
        :param literal: literal being evaluated
        """
        super().__init__(pp)
        self._literal = literal

    @property
    def literal(self):
        return self._literal

    def __repr__(self):
        return "{0.literal}".format(self)


class ExpressionAccess(Statement, metaclass=ABCMeta):
    """Expression access representation."""

    def __init__(self, pp, typ: LyraType):
        """Expression access construction.

        :param pp: program point associated with the statement
        :param typ: type of the expression
        """
        super().__init__(pp)
        self._typ = typ

    @property
    def typ(self):
        return self._typ


class VariableAccess(ExpressionAccess):
    """Variable access representation."""

    def __init__(self, pp, typ, variable: VariableIdentifier):
        """Variable access construction.

        :param pp: program point associated with the variable access
        :param typ: type of the variable
        :param variable: variable being accessed
        """
        super().__init__(pp, typ)
        self._variable = variable

    @property
    def variable(self):
        return self._variable

    def __repr__(self):
        return "{0.variable}".format(self)


class ListDisplayAccess(ExpressionAccess):
    """List display access representation."""

    def __init__(self, pp, typ, items: List[Statement]):
        """List display access construction.

        :param pp: program point associated with the list display access
        :param typ: type of the list
        :param items: list of items being displayed
        """
        super().__init__(pp, typ)
        self._items = items

    @property
    def items(self):
        return self._items

    def __repr__(self):
        return str(self.items)


class TupleDisplayAccess(ExpressionAccess):
    """Tuple display (= expression list with comma, or ()) access representation."""

    def __init__(self, pp, typ, items: List[Statement]):
        """tuple access construction.

        :param pp: program point associated with the tuple access
        :param typ: type of the tuple
        :param items: list of items being displayed
        """
        super().__init__(pp, typ)
        self._items = items

    @property
    def items(self):
        return self._items

    def __repr__(self):
        str_items = map(str, self.items)
        return '(' + ', '.join(str_items) + ')'


class SetDisplayAccess(ExpressionAccess):
    """Set display access representation."""
    def __init__(self, pp, typ, items: List[Statement]):
        """Set display access construction.

        :param pp: program point associated with the set display access
        :param typ: type of the set
        :param items: list of items being displayed
        """
        super().__init__(pp, typ)
        self._items = items

    @property
    def items(self):
        return self._items

    def __repr__(self):
        str_items = map(str, self.items)
        return '{' + ', '.join(str_items) + '}'


class DictDisplayAccess(ExpressionAccess):
    """Dictionary display access representation."""
    def __init__(self, pp, typ, keys: List[Statement], values: List[Statement]):
        """Dictionary display access construction.

        :param pp: program point associated with the list display access
        :param typ: type of the dictionary
        :param keys: list of keys being displayed
        :param values: list of values being displayed
        """
        super().__init__(pp, typ)
        self._keys = keys
        self._values = values

    @property
    def keys(self):
        return self._keys

    @property
    def values(self):
        return self._values

    def __repr__(self):
        str_keys = map(str, self.keys)
        str_values = map(str, self.values)
        return '{' + ', '.join(': '.join(x) for x in zip(str_keys, str_values)) + '}'


class SubscriptionAccess(ExpressionAccess):
    """Subscription access representation."""

    def __init__(self, pp, typ, target: Statement, key: Statement):
        """Subscription access construction.

        :param pp: program point associated with the subscription access
        :param typ: type of the subscription
        :param target: target of the subscription access
        :param key: index at which the target is begin subscripted
        """
        super().__init__(pp, typ)
        self._target = target
        self._key = key

    @property
    def target(self):
        return self._target

    @property
    def key(self):
        return self._key

    def __repr__(self):
        return "{0.target}[{0.key}]".format(self)


class SlicingAccess(ExpressionAccess):
    """Slicing access representation."""

    def __init__(self, pp, typ, target: Statement, lower: Statement, upper=None, stride=None):
        """Slicing access construction.

        :param pp: program point associated with the slicing access
        :param typ: type of the slicing
        :param target: target of the slicing access
        :param lower: lower bound of the slicing
        :param upper: upper bound of the slicing
        :param stride: step of the slicing
        """
        super().__init__(pp, typ)
        self._target: Statement = target
        self._lower: Statement = lower
        self._upper: Statement = upper
        self._stride: Statement = stride

    @property
    def target(self):
        return self._target

    @property
    def lower(self):
        return self._lower

    @property
    def upper(self):
        return self._upper

    @property
    def stride(self):
        return self._stride

    def __repr__(self):
        target = "{}[".format(self.target)
        lower = "{}:".format(self.lower) if self.lower else ":"
        upper = "{}".format(self.upper) if self.upper else ""
        stride = ":{}".format(self.stride) if self.stride else ""
        return target + lower + upper + stride + "]"

class AttributeAccess(ExpressionAccess):
    """Attribute access representation."""

    def __init__(self, pp, typ, target: Statement, attr: AttributeIdentifier):
        """Attribute access construction.

        :param pp: program point associated with the slicing access
        :param typ: type of the attribute
        :param target: object that contains the attribute
        :param attr: name of the attribute being accessed
        """
        super().__init__(pp, typ)
        self._target: Statement = target
        self._attr: AttributeIdentifier = attr

    @property
    def target(self):
        return self._target

    @property
    def attr(self):
        return self._attr

    def __repr__(self):
        return "{}.{}".format(self.target, self.attr)


"""
Assignment Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#assignment-statements
"""


class Assignment(Statement):
    """Assignment Statements.

    https://docs.python.org/3.4/reference/simple_stmts.html#assignment-statements
    """

    def __init__(self, pp, left: ExpressionAccess, right: Statement):
        """Assignment statement representation.

        :param pp: program point associated with the statement
        :param left: left-hand side of the assignment
        :param right: right-hand side of the assignment
        """
        super().__init__(pp)
        self._left = left
        self._right = right

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def __repr__(self):
        return "{0.left}: {0.left.typ} = {0.right}".format(self)


"""
Return Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#the-return-statement
"""


class Return(Statement):
    def __init__(self, pp, values: List[Statement]):
        """Return statement representation.

        :param pp: program point associated with the return
        :param values: list of returned expressions
        """
        super().__init__(pp)
        self._values = values

    @property
    def values(self):
        return self._values

    def __repr__(self):
        values = ', '.join('{}'.format(value) for value in self.values)
        values = '({})'.format(values) if len(self.values) > 1 else values
        return 'return {}'.format(values)


"""
Raise Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#the-raise-statement
"""


class Raise(Statement):
    def __init__(self, pp):
        """Raise statement representation.

        :param pp: program point associated with the raise
        """
        super().__init__(pp)

    def __repr__(self):
        return "raise Exception"


"""
Import Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#the-import-statement
"""


class Import(Statement):

    def __init__(self, pp, library: str, name: str):
        super().__init__(pp)
        self._library = library
        self._name = name

    @property
    def library(self):
        return self._library

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return "import {} as {}".format(self.library, self.name)


"""
Call Statements.
"""


class Call(Statement):
    def __init__(self, pp, name: str, arguments: List[Statement], typ: LyraType, forloop=False):
        """Call statement representation.

        :param pp: program point associated with the call
        :param name: name of the function/method being called
        :param arguments: list of arguments of the call
        :param typ: return type of the call
        :param forloop: whether the call happens in a for loop condition (default: False)
        """
        super().__init__(pp)
        self._name: str = name
        self._arguments: List[Statement] = arguments
        self._typ: LyraType = typ
        self._forloop: bool = forloop

    @property
    def name(self):
        return self._name

    @property
    def arguments(self):
        return self._arguments

    @property
    def typ(self):
        return self._typ

    @property
    def forloop(self):
        return self._forloop

    def __repr__(self):
        arguments = ", ".join("{}".format(argument) for argument in self.arguments)
        return "{}({})".format(self.name, arguments)
