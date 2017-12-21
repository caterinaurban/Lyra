"""
Expressions
===========

Lyra's internal representation of Python expressions.

:Authors: Caterina Urban and Simon Wehrli
"""

from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import Set, List

from lyra.core.types import LyraType, StringLyraType, IntegerLyraType, BooleanLyraType
from lyra.core.utils import copy_docstring


class Expression(metaclass=ABCMeta):
    """Expression representation.

    https://docs.python.org/3.4/reference/expressions.html
    """
    def __init__(self, typ: LyraType):
        """Expression construction.

        :param typ: type of the expression
        """
        self._typ = typ

    @property
    def typ(self):
        return self._typ

    @abstractmethod
    def __eq__(self, other: 'Expression'):
        """Expression equality.
        
        :param other: other expression to compare
        :return: whether the expression equality holds
        """

    @abstractmethod
    def __hash__(self):
        """Expression hash representation.
        
        :return: hash value representing the expression
        """

    def __ne__(self, other: 'Expression'):
        return not (self == other)

    @abstractmethod
    def __str__(self):
        """Expression string representation.
        
        :return: string representing the expression
        """

    def ids(self) -> Set['VariableIdentifier']:
        """Identifiers that appear in the expression.
        
        :return: set of identifiers that appear in the expression
        """
        ids = set()
        for expr in _walk(self):
            if isinstance(expr, VariableIdentifier):
                ids.add(expr)
        return ids


def _iter_child_exprs(expr: Expression):
    """
    Yield all direct child expressions of ``expr``,
    that is, all fields that are expressions
    and all items of fields that are lists of expressions.
    """
    for _, field in expr.__dict__.items():
        if isinstance(field, Expression):
            yield field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, Expression):
                    yield item


def _walk(expr: Expression):
    """
    Recursively yield all expressions in an expression tree
    starting at ``expr`` (including ``expr`` itself),
    in no specified order.
    """
    from collections import deque
    todo = deque([expr])
    while todo:
        expr = todo.popleft()
        todo.extend(_iter_child_exprs(expr))
        yield expr


# noinspection PyPep8Naming
class ExpressionVisitor(metaclass=ABCMeta):
    """
    An expression visitor base class that walks the expression tree and calls a
    visitor function for every expression found.  This function may return a value
    which is forwarded by the `visit` method.

    Subclasses are meant to implement the visitor functions.
    The visitor function for an expression is ``'visit_'`` +
    class name of the expression.  So a `Literal` expression visit function would
    be `visit_Literal`.  If no visitor function exists for an expression
    a `NotImplementedError` is raised.

    Adapted from `ast.py`.
    """
    def visit(self, expr, *args, **kwargs):
        """Visit of an expression."""
        method = 'visit_' + expr.__class__.__name__
        if hasattr(self, method):
            return getattr(self, method)(expr, *args, **kwargs)
        error = f"Missing visitor for {expr.__class__.__name__} in {self.__class__.__qualname__}!"
        raise NotImplementedError(error)

    @abstractmethod
    def visit_Literal(self, expr: 'Literal'):
        """Visit of a literal expression."""

    @abstractmethod
    def visit_Input(self, expr: 'Input'):
        """Visit of an input expression."""

    @abstractmethod
    def visit_VariableIdentifier(self, expr: 'VariableIdentifier'):
        """Visit of a variable identifier."""

    @abstractmethod
    def visit_ListDisplay(self, expr: 'ListDisplay'):
        """Visit of a list display."""

    @abstractmethod
    def visit_AttributeReference(self, expr: 'AttributeReference'):
        """Visit of an attribute reference."""

    @abstractmethod
    def visit_Subscription(self, expr: 'Subscription'):
        """Visit of a subscription expression."""

    @abstractmethod
    def visit_Slicing(self, expr: 'Slicing'):
        """Visit of a slicing expression."""

    @abstractmethod
    def visit_Call(self, expr: 'Call'):
        """Visit of a call expression."""

    @abstractmethod
    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation'):
        """Visit of a unary arithmetic operation."""

    @abstractmethod
    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation'):
        """Visit of a unary boolean operation."""

    @abstractmethod
    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation'):
        """Visit of a binary arithmetic operation."""

    @abstractmethod
    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation'):
        """Visit of a binary boolean operation."""

    @abstractmethod
    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation'):
        """Visit of a binary comparison operation."""

    def generic_visit(self, expr, *args, **kwargs):
        raise ValueError(
            f"{self.__class__.__qualname__} does not support generic visit of expressions! "
            f"Define handling for a {expr.__class__.__name__} expression explicitly!")


class NegationFreeNormalExpression(ExpressionVisitor):
    """
    An expression visitor that:

    1. removes negations using De Morgan's law, and

    2. puts in the normal form ``expr <= 0``
    all boolean comparison operations with ``=``, ``!=``, ``<``, ``<=``, ``>``, and ``>=`` .
    """

    @copy_docstring(ExpressionVisitor.visit_Literal)
    def visit_Literal(self, expr: 'Literal', invert=False):
        return expr    # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Input)
    def visit_Input(self, expr: 'Input', invert=False):
        return expr

    @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
    def visit_VariableIdentifier(self, expr: 'VariableIdentifier', invert=False):
        if isinstance(expr.typ, BooleanLyraType) and invert:
            operator = UnaryBooleanOperation.Operator.Neg
            return UnaryBooleanOperation(BooleanLyraType(), operator, expr)
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_ListDisplay)
    def visit_ListDisplay(self, expr: 'ListDisplay', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_AttributeReference)
    def visit_AttributeReference(self, expr: 'AttributeReference', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Subscription)
    def visit_Subscription(self, expr: 'Subscription', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Slicing)
    def visit_Slicing(self, expr: 'Slicing', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Call)
    def visit_Call(self, expr: 'Call', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', invert=False):
        if expr.operator == UnaryBooleanOperation.Operator.Neg:
            return self.visit(expr.expression, invert=not invert)
        raise ValueError(f"Unary boolean operator {expr.operator} is unsupported!")

    @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', invert=False):
        left = self.visit(expr.left, invert)
        operator = expr.operator.reverse_operator() if invert else expr.operator
        right = self.visit(expr.right, invert)
        return BinaryBooleanOperation(expr.typ, left, operator, right)

    @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation', invert=False):
        left = expr.left
        operator = expr.operator.reverse_operator() if invert else expr.operator
        right = expr.right
        if operator == BinaryComparisonOperation.Operator.Eq:
            # left = right -> left - right <= 0 && right - left <= 0
            zero = Literal(IntegerLyraType(), "0")
            minus = BinaryArithmeticOperation.Operator.Sub
            operator = BinaryComparisonOperation.Operator.LtE
            expr1 = BinaryArithmeticOperation(left.typ, left, minus, right)
            expr1 = BinaryComparisonOperation(expr.typ, expr1, operator, zero)
            expr2 = BinaryArithmeticOperation(right.typ, right, minus, left)
            expr2 = BinaryComparisonOperation(expr.typ, expr2, operator, zero)
            conjunction = BinaryBooleanOperation.Operator.And
            return BinaryBooleanOperation(expr.typ, expr1, conjunction, expr2)
        elif operator == BinaryComparisonOperation.Operator.NotEq:
            # left != right -> left - (right - 1) <= 0 || right - (left - 1) <= 0
            zero = Literal(IntegerLyraType(), "0")
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            operator = BinaryComparisonOperation.Operator.LtE
            expr1 = BinaryArithmeticOperation(right.typ, right, minus, one)
            expr1 = BinaryArithmeticOperation(left.typ, left, minus, expr1)
            expr1 = BinaryComparisonOperation(expr.typ, expr1, operator, zero)
            expr2 = BinaryArithmeticOperation(left.typ, left, minus, one)
            expr2 = BinaryArithmeticOperation(right.typ, right, minus, expr2)
            expr2 = BinaryComparisonOperation(expr.typ, expr2, operator, zero)
            disjunction = BinaryBooleanOperation.Operator.Or
            return BinaryBooleanOperation(expr.typ, expr1, disjunction, expr2)
        elif operator == BinaryComparisonOperation.Operator.Lt:
            # left < right -> left - (right - 1) <= 0
            zero = Literal(IntegerLyraType(), "0")
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            right = BinaryArithmeticOperation(right.typ, right, minus, one)
            left = BinaryArithmeticOperation(left.typ, left, minus, right)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, left, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.LtE:
            # left <= right -> left - right <= 0
            zero = Literal(IntegerLyraType(), "0")
            minus = BinaryArithmeticOperation.Operator.Sub
            left = BinaryArithmeticOperation(left.typ, left, minus, right)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, left, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.Gt:
            # left > right -> right - (left - 1) <= 0
            zero = Literal(IntegerLyraType(), "0")
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            left = BinaryArithmeticOperation(left.typ, left, minus, one)
            right = BinaryArithmeticOperation(right.typ, right, minus, left)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, right, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.GtE:
            # left >= right -> right - left <= 0
            zero = Literal(IntegerLyraType(), "0")
            minus = BinaryArithmeticOperation.Operator.Sub
            right = BinaryArithmeticOperation(right.typ, right, minus, left)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, right, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.In:
            return BinaryComparisonOperation(expr.typ, left, operator, right)
        elif operator == BinaryComparisonOperation.Operator.NotIn:
            return BinaryComparisonOperation(expr.typ, left, operator, right)
        raise ValueError(f"Boolean comparison operator {expr} is unsupported!")


"""
Atomic Expressions
https://docs.python.org/3.4/reference/expressions.html#atoms
"""


class Literal(Expression):
    """Literal representation.

    https://docs.python.org/3.4/reference/expressions.html#literals
    """
    def __init__(self, typ: LyraType, val: str):
        """Literal construction.

        :param typ: type of the literal
        :param val: value of the literal
        """
        super().__init__(typ)
        self._val = val

    @property
    def val(self):
        return self._val

    def __eq__(self, other):
        return (self.typ, self.val) == (other.typ, other.val)

    def __hash__(self):
        return hash((self.typ, self.val))

    def __str__(self):
        if isinstance(self.typ, StringLyraType):
            return f'"{self.val}"'
        return f"{self.val}"


class Identifier(Expression):
    """Identifier representation.

    https://docs.python.org/3.4/reference/expressions.html#atom-identifiers
    """
    def __init__(self, typ: LyraType, name: str):
        """Identifier construction.

        :param typ: type of the identifier
        :param name: name of the identifier
        """
        super().__init__(typ)
        self._name = name

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return "{0.name}".format(self)


class VariableIdentifier(Identifier):
    """Variable identifier representation."""
    def __init__(self, typ: LyraType, name: str):
        """Variable identifier construction.
        
        :param typ: type of the identifier
        :param name: name of the identifier
        """
        super().__init__(typ, name)


class LengthIdentifier(Identifier):
    """Sequence or collection length representation."""
    def __init__(self, variable: VariableIdentifier):
        """Sequence or collection length construction.

        :param variable: sequence or collection the length of which is being constructed
        """
        name = "len({0.name})".format(variable)
        super().__init__(IntegerLyraType(), name)


class ListDisplay(Expression):
    """List display representation.
    
    https://docs.python.org/3/reference/expressions.html#list-displays
    """

    def __init__(self, typ: LyraType, items: List[Expression] = None):
        """List display construction.
        
        :param typ: type of the list
        :param items: list of items being displayed
        """
        super().__init__(typ)
        self._items = items or []

    @property
    def items(self):
        return self._items

    def __eq__(self, other):
        return (self.typ, self.items) == (other.typ, other.items)

    def __hash__(self):
        return hash((self.typ, str(self.items)))

    def __str__(self):
        return str(self.items)


class Input(Expression):
    """Input expression representation."""
    def __init__(self, typ: LyraType):
        """Input expression construction.

        :param typ: type of the input
        """
        super().__init__(typ)

    def __eq__(self, other):
        return self.typ == other.typ

    def __hash__(self):
        return hash(self.typ)

    def __str__(self):
        return "input()"


"""
Primary Expressions
https://docs.python.org/3.4/reference/expressions.html#primaries
"""


class AttributeReference(Expression):
    """Attribute reference representation.

    https://docs.python.org/3.4/reference/expressions.html#attribute-references
    """
    def __init__(self, typ: LyraType, target: Expression, attribute: Identifier):
        """Attribute reference construction.
        
        :param typ: type of the attribute
        :param target: object the attribute of which is being referenced
        :param attribute: attribute being referenced
        """
        super().__init__(typ)
        self._target = target
        self._attribute = attribute

    @property
    def target(self):
        return self._target

    @property
    def attribute(self):
        return self._attribute

    def __eq__(self, other):
        typ = self.typ == other.typ
        target = self.target == other.target
        attribute = self.attribute == other.attribute
        return typ and target and attribute

    def __hash__(self):
        return hash((self.typ, self.target, self.attribute))

    def __str__(self):
        return "{0.target}.{0.attribute}".format(self)


class Subscription(Expression):
    """Subscription representation.

    https://docs.python.org/3.4/reference/expressions.html#subscriptions
    """
    def __init__(self, typ: LyraType, target: Expression, key: Expression):
        """Subscription construction.

        :param typ: type of the subscription
        :param target: object being subject to subscription
        :param key: index at which the object is subscripted
        """
        super().__init__(typ)
        self._target = target
        self._key = key

    @property
    def target(self):
        return self._target

    @property
    def key(self):
        return self._key

    def __eq__(self, other):
        typ = self.typ == other.typ
        target = self.target == other.target
        key = self.key == other.key
        return typ and target and key

    def __hash__(self):
        return hash((self.typ, self.target, self.key))

    def __str__(self):
        return "{0.target}[{0.key}]".format(self)


class Slicing(Expression):
    """Slicing representation.

    https://docs.python.org/3.4/reference/expressions.html#slicings
    """
    def __init__(self, typ: LyraType, target: Expression,
                 lower: Expression, upper: Expression, stride: Expression = None):
        """Slicing construction.

        :param typ: type of the slicing
        :param target: object being subject to slicing
        :param lower: lower bound of the slicing
        :param upper: upper bound of the slicing
        :param stride: stride of the slicing
        """
        super().__init__(typ)
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

    def __eq__(self, other):
        typ = self.typ == other.typ
        target = self.target == other.target
        lower = self.lower == other.lower
        upper = self.upper == other.upper
        stride = self.stride == other.stride
        return typ and target and lower and upper and stride

    def __hash__(self):
        return hash((self.typ, self.target, self.lower, self.upper, self.stride))

    def __str__(self):
        if self.stride:
            return "{0.target}[{0.lower}:{0.upper}:{0.stride}]".format(self)
        return "{0.target}[{0.lower}:{0.upper}]".format(self)


class Call(Expression):
    """Call representation.

    https://docs.python.org/3.4/reference/expressions.html#calls
    """
    def __init__(self, typ: LyraType, name: str, arguments: List[Expression]):
        """Call construction

        :param typ: type of the call
        :param name: name of the call
        :param arguments: arguments of the call
        """
        super().__init__(typ)
        self._name = name
        self._arguments = arguments

    @property
    def name(self):
        return self._name

    @property
    def arguments(self):
        return self._arguments

    def __eq__(self, other):
        typ =  self.typ == other.typ
        name = self.name == other.name
        arguments = self.arguments == other.arguments
        return typ and name and arguments

    def __hash__(self):
        return hash((self.typ, self.name, self.arguments))

    def __str__(self):
        comma_sep_args = ", ".join(self.arguments)
        return f"{self.name}({comma_sep_args})"

"""
Operation Expressions
"""


class Operation(Expression, metaclass=ABCMeta):
    """Operation representation."""


"""
Unary Operation Expressions
"""


class UnaryOperation(Operation):
    """Unary operation representation."""
    class Operator(IntEnum):
        """Unary operator representation."""

        @abstractmethod
        def __str__(self):
            """Unary operator string representation.
            
            :return: string representing the operator
            """

    def __init__(self, typ: LyraType, operator: Operator, expression: Expression):
        """Unary operation construction.
        
        :param typ: type of the operation
        :param operator: operator of the operation
        :param expression: expression of the operation 
        """
        super().__init__(typ)
        self._operator = operator
        self._expression = expression

    @property
    def operator(self):
        return self._operator

    @property
    def expression(self):
        return self._expression

    def __eq__(self, other):
        typ = self.typ == other.typ
        operator = self.operator == other.operator
        expression = self.expression == other.expression
        return typ and operator and expression

    def __hash__(self):
        return hash((self.typ, self.operator, self.expression))

    def __str__(self):
        expr_string = str(self.expression)
        if isinstance(self.expression, Operation):
            expr_string = f"({expr_string})"
        return f"{str(self.operator)}{expr_string}"


class UnaryArithmeticOperation(UnaryOperation):
    """Unary arithmetic operation expression representation.
    
    https://docs.python.org/3.4/reference/expressions.html#unary-arithmetic-and-bitwise-operations
    """

    class Operator(UnaryOperation.Operator):
        """Unary arithmetic operator representation."""
        Add = 1
        Sub = -1

        def __str__(self):
            if self.value == 1:
                return "+"
            elif self.value == -1:
                return "-"

    def __init__(self, typ: LyraType, operator: Operator, expression: Expression):
        """Unary arithmetic operation expression representation.
        
        :param typ: type of the operation
        :param operator: operator of the operation
        :param expression: expression of the operation 
        """
        super().__init__(typ, operator, expression)


class UnaryBooleanOperation(UnaryOperation):
    """Unary boolean operation expression representation.
    
    https://docs.python.org/3.4/reference/expressions.html#boolean-operations
    """

    class Operator(UnaryOperation.Operator):
        """Unary boolean operator representation."""
        Neg = 1

        def __str__(self):
            if self.value == 1:
                return "not"

    def __init__(self, typ: LyraType, operator: Operator, expression: Expression):
        """Unary boolean operation expression representation.
        
        :param typ: type of the operation
        :param operator: operator of the operation
        :param expression: expression of the operation 
        """
        super().__init__(typ, operator, expression)


"""
Binary Operation Expressions
"""


class BinaryOperation(Operation):
    """Binary operation representation."""
    class Operator(IntEnum):
        """Binary operator representation."""

        @abstractmethod
        def __str__(self):
            """Binary operator string representation.

            :return: string representing the operator
            """

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression):
        """Binary operation construction.
        
        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        """
        super().__init__(typ)
        self._left = left
        self._operator = operator
        self._right = right

    @property
    def left(self):
        return self._left

    @property
    def operator(self):
        return self._operator

    @property
    def right(self):
        return self._right

    def __eq__(self, other):
        typ = self.typ == other.typ
        left = self.left == other.left
        operator = self.operator == other.operator
        right = self.right == other.right
        return typ and left and operator and right

    def __hash__(self):
        return hash((self.typ, self.left, self.operator, self.right))

    def __str__(self):
        left_string = str(self.left)
        right_string = str(self.right)
        if isinstance(self.left, Operation):
            left_string = f"({left_string})"
        if isinstance(self.right, Operation):
            right_string = f"({right_string})"
        return f"{left_string} {str(self.operator)} {right_string}"


class BinaryArithmeticOperation(BinaryOperation):
    """Binary arithmetic operation expression representation.
    
    https://docs.python.org/3.4/reference/expressions.html#binary-arithmetic-operations
    """

    class Operator(BinaryOperation.Operator):
        """Binary arithmetic operator representation."""
        Add = 1
        Sub = 2
        Mult = 3
        Div = 4

        def __str__(self):
            if self.value == 1:
                return "+"
            elif self.value == 2:
                return "-"
            elif self.value == 3:
                return "*"
            elif self.value == 4:
                return "/"

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression):
        """Binary arithmetic operation expression representation.
        
        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        """
        super().__init__(typ, left, operator, right)


class BinaryBooleanOperation(BinaryOperation):
    """Binary boolean operation expression representation.
    
    https://docs.python.org/3.6/reference/expressions.html#boolean-operations
    """

    class Operator(BinaryOperation.Operator):
        """Binary arithmetic operator representation."""
        And = 1
        Or = 2

        def reverse_operator(self):
            """Returns the reverse operator of this operator."""
            if self.value == 1:
                return BinaryBooleanOperation.Operator.Or
            elif self.value == 2:
                return BinaryBooleanOperation.Operator.And

        def __str__(self):
            return self.name.lower()

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression):
        """Binary boolean operation expression representation.

        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        """
        super().__init__(typ, left, operator, right)


class BinaryComparisonOperation(BinaryOperation):
    """Binary comparison operation expression representation.
    
    https://docs.python.org/3.4/reference/expressions.html#comparisons
    """

    class Operator(BinaryOperation.Operator):
        """Binary comparison operator representation"""
        Eq = 1
        NotEq = 2
        Lt = 3
        LtE = 4
        Gt = 5
        GtE = 6
        Is = 7
        IsNot = 8
        In = 9
        NotIn = 10

        def reverse_operator(self):
            """Returns the reverse operator of this operator."""
            if self.value == 1:
                return BinaryComparisonOperation.Operator.NotEq
            elif self.value == 2:
                return BinaryComparisonOperation.Operator.Eq
            elif self.value == 3:
                return BinaryComparisonOperation.Operator.GtE
            elif self.value == 4:
                return BinaryComparisonOperation.Operator.Gt
            elif self.value == 5:
                return BinaryComparisonOperation.Operator.LtE
            elif self.value == 6:
                return BinaryComparisonOperation.Operator.Lt
            elif self.value == 7:
                return BinaryComparisonOperation.Operator.IsNot
            elif self.value == 8:
                return BinaryComparisonOperation.Operator.Is
            elif self.value == 9:
                return BinaryComparisonOperation.Operator.NotIn
            elif self.value == 10:
                return BinaryComparisonOperation.Operator.In

        def __str__(self):
            if self.value == 1:
                return "=="
            elif self.value == 2:
                return "!="
            elif self.value == 3:
                return "<"
            elif self.value == 4:
                return "<="
            elif self.value == 5:
                return ">"
            elif self.value == 6:
                return ">="
            elif self.value == 7:
                return "is"
            elif self.value == 8:
                return "is not"
            elif self.value == 9:
                return "in"
            elif self.value == 10:
                return "not in"

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression):
        """Binary comparison operation expression representation.

        :param typ: type of the operation
        :param left: left expression of the operation
        :param operator: operator of the operation
        :param right: right expression of the operation
        """
        super().__init__(typ, left, operator, right)


