"""
Statements
==========

Lyra's internal representation of Python statements.

:Authors: Caterina Urban and Simon Wehrli
"""

from abc import ABCMeta, abstractmethod
from typing import List

from lyra.core.expressions import Expression, VariableIdentifier
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


"""
Expression Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#expression-statements
"""


class LiteralEvaluation(Statement):
    """Literal evaluation expression."""

    def __init__(self, pp: ProgramPoint, literal: Expression):
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
    """Statement representation for statements that
    can appear on the left-hand side of assignments."""


class VariableAccess(ExpressionAccess):
    """Variable access representation."""

    def __init__(self, pp: ProgramPoint, variable: VariableIdentifier):
        """Variable access construction.

        :param pp: program point associated with the variable access
        :param variable: variable being accessed
        """
        super().__init__(pp)
        self._variable = variable

    @property
    def variable(self):
        return self._variable

    def __repr__(self):
        return "{0.variable}".format(self)


class ListDisplayAccess(ExpressionAccess):
    """List display access representation."""

    def __init__(self, pp: ProgramPoint, items: List[Statement]):
        """List display access construction.

        :param pp: program point associated with the list display access
        :param items: list of items being displayed
        """
        super().__init__(pp)
        self._items = items

    @property
    def items(self):
        return self._items

    def __repr__(self):
        return str(self.items)


class SubscriptionAccess(ExpressionAccess):
    """Subscription access representation."""

    def __init__(self, pp: ProgramPoint, target: Statement, key: Statement):
        """Subscription access construction.

        :param pp: program point associated with the subscription access
        :param target: target of the subscription access
        :param key: index at which the target is begin subscripted
        """
        super().__init__(pp)
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

    def __init__(self, pp: ProgramPoint, target: Statement,
                 lower: Statement, upper: Statement, stride: Statement = None):
        super().__init__(pp)
        self._target = target
        self._lower = lower
        self._upper = upper
        self._stride = stride

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
        if self.stride:
            return "{0.target}[{0.lower}:{0.upper}:{0.stride}]".format(self)
        return "{0.target}[{0.lower}:{0.upper}]".format(self)


class Call(Statement):
    def __init__(self, pp: ProgramPoint, name: str, arguments: List[Statement], typ: LyraType):
        """Call statement representation.

        :param pp: program point associated with the call
        :param name: name of the function/method being called
        :param arguments: list of arguments of the call
        :param typ: return type of the call
        """
        super().__init__(pp)
        self._name = name
        self._arguments = arguments
        self._typ = typ

    @property
    def name(self):
        return self._name

    @property
    def arguments(self):
        return self._arguments

    @property
    def typ(self):
        return self._typ

    def __repr__(self):
        arguments = ", ".join("{}".format(argument) for argument in self.arguments)
        return "{}({})".format(self.name, arguments)


class Raise(Statement):
    def __init__(self, pp: ProgramPoint, exception: Call):
        """Call statement representation.

        :param pp: program point associated with the call
        """
        super().__init__(pp)
        self._exception = exception

    def __repr__(self):
        if isinstance(self.exception, Call):
            arguments = ", ".join("{}".format(argument) for argument in self.exception.arguments)
            return f"raise {self.exception.name}({arguments})"
        else:
            return f"raise {self.exception.variable.name}"

    @property
    def exception(self):
        return self._exception


"""
Assignment Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#assignment-statements
"""


class Assignment(Statement):
    """Assignment Statements.

    https://docs.python.org/3.4/reference/simple_stmts.html#assignment-statements
    """

    def __init__(self, pp: ProgramPoint, left: ExpressionAccess, right: Statement):
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
        return "{0.left} = {0.right}".format(self)
