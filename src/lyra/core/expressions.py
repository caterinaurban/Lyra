from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import Set, Sequence
from lyra.core.types import LyraType, StringLyraType, IntegerLyraType, BooleanLyraType
from lyra.core.utils import copy_docstring

"""
Expressions.
https://docs.python.org/3.4/reference/expressions.html
"""


class Expression(metaclass=ABCMeta):
    def __init__(self, typ: LyraType):
        """Expression representation.
        https://docs.python.org/3.4/reference/expressions.html
        
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

    def ids(self) -> Set['Expression']:
        """Identifiers that appear in the expression.
        
        :return: set of identifiers that appear in the expression
        """
        from lyra.core.expressions_tools import walk
        ids = set()
        for e in walk(self):
            if isinstance(e, VariableIdentifier):
                ids.add(e)
        return ids


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
        raise NotImplementedError(f"Missing visitor for {expr.__class__.__name__} in {self.__class__.__qualname__}!")

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
    def visit_Slice(self, expr: 'Slice'):
        """Visit of a slice expression."""

    @abstractmethod
    def visit_Index(self, expr: 'Index'):
        """Visit of an index expression."""

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

    (1) removes negations using De Morgan's law, and

    (2) puts all boolean comparison operations in the normal form ``expr <= 0``.

    .. note:: The only supported boolean comparison operators are ``=``, ``!=``, ``<``, ``<=``, ``>``, and ``>=``.
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
            return UnaryBooleanOperation(BooleanLyraType(), UnaryBooleanOperation.Operator.Neg, expr)
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_ListDisplay)
    def visit_ListDisplay(self, expr: 'ListDisplay', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_AttributeReference)
    def visit_AttributeReference(self, expr: 'AttributeReference', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Slice)
    def visit_Slice(self, expr: 'Slice', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_Index)
    def visit_Index(self, expr: 'Index', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation', invert=False):
        return expr     # nothing to be done

    @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', invert=False):
        if expr.operator == UnaryBooleanOperation.Operator.Neg:
            return self.visit(expr.expression, invert=not invert)
        raise ValueError(f"Unary boolean operator {expr} is unsupported!")

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
        zero = Literal(IntegerLyraType(), "0")
        if operator == BinaryComparisonOperation.Operator.Eq:  # left = right -> left - right <= 0 && right - left <= 0
            minus = BinaryArithmeticOperation.Operator.Sub
            operator = BinaryComparisonOperation.Operator.LtE
            expr1 = BinaryArithmeticOperation(left.typ, left, minus, right)
            expr1 = BinaryComparisonOperation(expr.typ, expr1, operator, zero)
            expr2 = BinaryArithmeticOperation(right.typ, right, minus, left)
            expr2 = BinaryComparisonOperation(expr.typ, expr2, operator, zero)
            return BinaryBooleanOperation(expr.typ, expr1, BinaryBooleanOperation.Operator.And, expr2)
        elif operator == BinaryComparisonOperation.Operator.NotEq:
            # left != right -> left - (right - 1) <= 0 || right - (left - 1) <= 0
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            operator = BinaryComparisonOperation.Operator.LtE
            expr1 = BinaryArithmeticOperation(right.typ, right, minus, one)
            expr1 = BinaryArithmeticOperation(left.typ, left, minus, expr1)
            expr1 = BinaryComparisonOperation(expr.typ, expr1, operator, zero)
            expr2 = BinaryArithmeticOperation(left.typ, left, minus, one)
            expr2 = BinaryArithmeticOperation(right.typ, right, minus, expr2)
            expr2 = BinaryComparisonOperation(expr.typ, expr2, operator, zero)
            return BinaryBooleanOperation(expr.typ, expr1, BinaryBooleanOperation.Operator.Or, expr2)
        elif operator == BinaryComparisonOperation.Operator.Lt:    # left < right -> left - (right - 1) <= 0
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            right = BinaryArithmeticOperation(right.typ, right, minus, one)
            left = BinaryArithmeticOperation(left.typ, left, minus, right)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, left, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.LtE:   # left <= right -> left - right <= 0
            minus = BinaryArithmeticOperation.Operator.Sub
            left = BinaryArithmeticOperation(left.typ, left, minus, right)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, left, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.Gt:    # left > right -> right - (left - 1) <= 0
            one = Literal(IntegerLyraType(), "1")
            minus = BinaryArithmeticOperation.Operator.Sub
            left = BinaryArithmeticOperation(left.typ, left, minus, one)
            right = BinaryArithmeticOperation(right.typ, right, minus, left)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, right, operator, zero)
        elif operator == BinaryComparisonOperation.Operator.GtE:   # left >= right -> right - left <= 0
            minus = BinaryArithmeticOperation.Operator.Sub
            right = BinaryArithmeticOperation(right.typ, right, minus, left)
            operator = BinaryComparisonOperation.Operator.LtE
            return BinaryComparisonOperation(expr.typ, right, operator, zero)
        raise ValueError(f"Boolean comparison operator {expr} is unsupported!")


"""
Atomic Expressions
https://docs.python.org/3.4/reference/expressions.html#atoms
"""


class Literal(Expression):
    def __init__(self, typ: LyraType, val: str):
        """Literal expression representation.
        https://docs.python.org/3.4/reference/expressions.html#literals
        
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
        else:
            return f"{self.val}"


class Input(Expression):
    def __init__(self, typ: LyraType):
        """Input expression representation.

        :param typ: type of the input
        """
        super().__init__(typ)

    def __eq__(self, other):
        return self.typ == other.typ

    def __hash__(self):
        return hash(self.typ)

    def __str__(self):
        return "input()"


class Identifier(Expression):
    def __init__(self, typ: LyraType, name: str):
        """Identifier expression representation.
        https://docs.python.org/3.4/reference/expressions.html#atom-identifiers
        
        :param typ: type of the identifier
        :param name: name of the identifier
        """
        super().__init__(typ)
        self._name = name

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        return (self.typ, self.name) == (other.typ, other.name)

    def __hash__(self):
        return hash((self.typ, self.name))

    def __str__(self):
        return "{0.name}".format(self)


class VariableIdentifier(Identifier):
    def __init__(self, typ: LyraType, name: str):
        """Variable identifier expression representation.
        
        :param typ: type of the identifier
        :param name: name of the identifier
        """
        super().__init__(typ, name)


class ListDisplay(Expression):
    """List display
    
    https://docs.python.org/3/reference/expressions.html#list-displays
    """

    def __init__(self, typ: LyraType, items: Sequence[Expression] = None):
        """List display representation
        
        :param typ: type of the list display
        :param items: listed items
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


"""
Primary Expressions
https://docs.python.org/3.4/reference/expressions.html#primaries
"""


class AttributeReference(Expression):
    """Attribute reference expression representation.

    https://docs.python.org/3.4/reference/expressions.html#attribute-references
    """

    def __init__(self, typ: LyraType, primary: Expression, attribute: Identifier):
        """Attribute reference expression representation.
        
        :param typ: type of the attribute
        :param primary: object the attribute of which is being referenced
        :param attribute: attribute being referenced
        """
        super().__init__(typ)
        self._primary = primary
        self._attribute = attribute

    @property
    def primary(self):
        return self._primary

    @property
    def attribute(self):
        return self._attribute

    def __eq__(self, other):
        return (self.typ, self.primary, self.attribute) == (other.typ, other.primary, other.attribute)

    def __hash__(self):
        return hash((self.typ, self.primary, self.attribute))

    def __str__(self):
        return "{0.primary}.{0.attribute}".format(self)


class Slice(Expression):
    """Slice (list/dictionary access) representation.
    """

    def __init__(self, typ: LyraType, target: Expression, lower: Expression, step: Expression, upper: Expression):
        """Slice (list/dictionary access) representation.

        :param typ: type of the slice
        :param target
        :param lower
        :param upper
        :param step
        """
        super().__init__(typ)
        self._target = target
        self._lower = lower
        self._step = step
        self._upper = upper

    @property
    def target(self):
        return self._target

    @property
    def lower(self):
        return self._lower

    @property
    def step(self):
        return self._step

    @property
    def upper(self):
        return self._upper

    def __str__(self):
        if self.step:
            return "{}[{}:{}:{}]".format(self.target or "", self.lower, self.step, self.upper or "")
        else:
            return "{}[{}:{}]".format(self.target, self.lower or "", self.upper or "")

    def __eq__(self, other):
        return (self.typ, self.target, self.lower, self.step, self.upper) == (
            other.typ, other.target, other.lower, self.step, self.upper)

    def __hash__(self):
        return hash((self.typ, self.target, self.lower, self.step, self.upper))


class Index(Expression):
    """Index (list/dictionary access) representation.
    """

    def __init__(self, typ: LyraType, target: Expression, index: Expression):
        """Index  (list/dictionary access) representation.

        :param typ: type of the attribute
        :param target
        :param index
        """
        super().__init__(typ)
        self._target = target
        self._index = index

    @property
    def target(self):
        return self._target

    @property
    def index(self):
        return self._index

    def __str__(self):
        return "{}[{}]".format(self.target, self.index)

    def __eq__(self, other):
        return (self.typ, self.target, self.index) == (
            other.typ, other.target, other.index)

    def __hash__(self):
        return hash((self.typ, self.target, self.index))


"""
Generic Operation Expressions
"""


class Operation(Expression, metaclass=ABCMeta):
    pass


"""
Unary Operation Expressions
"""


class UnaryOperation(Operation):
    class Operator(IntEnum):
        """Unary operator representation."""

        @abstractmethod
        def __str__(self):
            """Unary operator string representation.
            
            :return: string representing the operator
            """

    def __init__(self, typ: LyraType, operator: Operator, expression: Expression):
        """Unary operation expression representation.
        
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
        return (self.typ, self.operator, self.expression) == (other.typ, other.operator, other.expression)

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
    class Operator(IntEnum):
        """Binary operator representation."""

        @abstractmethod
        def __str__(self):
            """Binary operator string representation.

            :return: string representing the operator
            """

    def __init__(self, typ: LyraType, left: Expression, operator: Operator, right: Expression):
        """Binary operation expression representation.
        
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
        return (self.typ, self.left, self.operator, self.right) == (other.typ, other.left, other.operator, other.right)

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
