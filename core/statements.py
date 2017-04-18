from abc import ABC, abstractmethod
from abstract_domains.state import State
from core.expressions import VariableIdentifier, Expression


class ProgramPoint(object):
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
        return str(self)

    def __str__(self):
        """Program point string representation

        :return: string representing the program point
        """
        return "[line:{0.line}, column:{0.column}]".format(self)


"""
Statements.
https://docs.python.org/3.4/reference/simple_stmts.html
"""


class Statement(ABC):
    def __init__(self, pp: ProgramPoint):
        """Statement representation.
        
        :param pp: program point associated with the statement  
        """
        self._pp = pp

    @property
    def pp(self):
        return self._pp

    def __repr__(self):
        return str(self)

    @abstractmethod
    def __str__(self):
        """Statement string representation.
        
        :return: string representing the statement
        """

    @abstractmethod
    def forward_semantics(self, state: State) -> State:
        """Abstract forward semantics of the statement. 
        
        :param state: state before the statement
        :return: modified state after the statement
        """

    @abstractmethod
    def backward_semantics(self, state: State) -> State:
        """Abstract backward semantics of the statement.
        
        :param state: state after the statement
        :return: modified state before the statement
        """


class VariableAccess(Statement):
    def __init__(self, pp: ProgramPoint, var: VariableIdentifier):
        """Variable access representation.

        :param pp: program point associated with the variable access
        :param var: variable being accessed
        """
        super().__init__(pp)
        self._var = var

    @property
    def var(self):
        return self._var

    def __str__(self):
        return "{0.var}".format(self)

    def semantics(self, state: State) -> State:
        return state.access_variable(self.var)

    def forward_semantics(self, state: State) -> State:
        return self.semantics(state)

    def backward_semantics(self, state: State) -> State:
        return self.semantics(state)


"""
Expression Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#expression-statements
"""


class ExpressionEvaluation(Statement):
    def __init__(self, pp: ProgramPoint, expression: Expression):
        """Expression evaluation representation.

        :param pp: program point associated with the expression evaluation
        :param expression: expression being evaluated
        """
        super().__init__(pp)
        self._expression = expression

    @property
    def expression(self):
        return self._expression

    def __str__(self):
        return "{0.expression}".format(self)

    def semantics(self, state: State) -> State:
        return state.evaluate_expression(self.expression)

    def forward_semantics(self, state: State) -> State:
        return self.semantics(state)

    def backward_semantics(self, state: State) -> State:
        return self.semantics(state)


"""
Assignment Statements.
https://docs.python.org/3.4/reference/simple_stmts.html#assignment-statements
"""


class Assignment(Statement):
    def __init__(self, pp: ProgramPoint, left: Statement, right: Statement):
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

    def __str__(self):
        return "{0.pp} {0.left} = {0.right}".format(self)

    def forward_semantics(self, state: State) -> State:
        lhs = self.left.forward_semantics(state).result    # lhs evaluation
        rhs = self.right.forward_semantics(state).result   # rhs evaluation
        if isinstance(self.left, VariableAccess):
            return state.assign_variable(lhs, rhs)
        else:
            raise NotImplementedError("Forward semantics for assignment {0!s} not yet implemented!".format(self))

    def backward_semantics(self, state: State) -> State:
        lhs = self.left.backward_semantics(state).result    # lhs evaluation
        rhs = self.right.backward_semantics(state).result   # rhs evaluation
        if isinstance(self.left, VariableAccess):
            return state.substitute_variable(lhs, rhs)
        else:
            raise NotImplementedError("Backward semantics for assignment {0!s} not yet implemented!".format(self))
