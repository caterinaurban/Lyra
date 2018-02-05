from lyra.abstract_domains.lattice import Lattice, BottomMixin
from lyra.core.expressions import VariableIdentifier, Literal, Expression, \
    BinaryArithmeticOperation, BinaryComparisonOperation, UnaryBooleanOperation, \
    UnaryArithmeticOperation, ListDisplay, LengthIdentifier, Identifier
from lyra.core.types import FloatLyraType, IntegerLyraType, BooleanLyraType
from lyra.core.utils import copy_docstring


class SimpleRelation:
    """Stores a relational constraint."""

    def __init__(self, first_pos, first, constant, second_pos, second):
        self.first_pos = first_pos
        self.first = first
        self.constant = constant
        self.second_pos = second_pos
        self.second = second

    @classmethod
    def from_expression(cls, expr: Expression):
        inverted = False
        if isinstance(expr, UnaryBooleanOperation):
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                inverted = True
                expr = expr.expression
        if isinstance(expr, BinaryComparisonOperation):
            if expr.operator == BinaryComparisonOperation.Operator.In:
                return None
            if isinstance(expr.left, Literal) or isinstance(expr.right, Literal):
                return None
            left_is_var = isinstance(expr.left, (VariableIdentifier, LengthIdentifier))
            right_is_var = isinstance(expr.right, (VariableIdentifier, LengthIdentifier))
            if left_is_var and right_is_var:
                is_lte = expr.operator == BinaryComparisonOperation.Operator.LtE
                is_lt = expr.operator == BinaryComparisonOperation.Operator.Lt
                is_gte = expr.operator == BinaryComparisonOperation.Operator.GtE
                is_gt = expr.operator == BinaryComparisonOperation.Operator.Gt
                if is_lte and not inverted or is_gt and inverted:
                    return cls(True, expr.left, 0, False, expr.right)
                if is_lt and not inverted or is_gte and inverted:
                    return cls(True, expr.left, 1, False, expr.right)
                if is_gte and not inverted or is_lt and inverted:
                    return cls(False, expr.left, 0, True, expr.right)
                if is_gt and not inverted or is_lte and inverted:
                    return cls(False, expr.left, 1, True, expr.right)
        return None

    def contains(self, var: VariableIdentifier) -> bool:
        """Checks if the relation contains the given variable.

        :param var: variable that is checked if it appears in the relation
        :return: if the variable appears in the relation
        """
        if self.first == var or self.second == var:
            return True
        length_var = LengthIdentifier(var)
        return self.first == length_var or self.second == length_var

    def substitute(self, var: Identifier, expr: 'SimpleExpression'):
        """Substitutes a variable in the current relation with the given expression

        :param var: variable that is substituted
        :param expr: expression the variable is substituted with
        """
        if self.first == var:
            self.first = expr.var
            is_pos = self.first_pos
        elif self.second == var:
            self.second = expr.var
            is_pos = self.second_pos
        elif isinstance(self.first, LengthIdentifier) and self.first.name == f"len({var.name})":
            self.first = LengthIdentifier(expr.var)
            is_pos = self.first_pos
        elif isinstance(self.second, LengthIdentifier) and self.second.name == f"len({var.name})":
            self.second = LengthIdentifier(expr.var)
            is_pos = self.second_pos
        else:
            return self

        if is_pos:
            self.constant += expr.const
        else:
            self.constant -= expr.const
        return self

    def __eq__(self, other: 'SimpleRelation'):
        same_first = self.first_pos == other.first_pos and self.first == other.first
        same_second = self.second_pos == other.second_pos and self.second == other.second
        same_const = self.constant == other.constant
        return same_first and same_second and same_const

    def __repr__(self):
        sign_first = "" if self.first_pos else "-"
        sign_other = "+" if self.second_pos else "-"
        sign_constant = "+" if self.constant >= 0 else "-"
        constant = self.constant if self.constant >= 0 else -self.constant
        rel = f"{sign_first}{self.first} {sign_other} {self.second} {sign_constant} {constant}"
        return f"{rel} <= 0"


class SimpleRelationsLattice(BottomMixin):
    """
    The Simple Relations Lattice consists of a list of SimpleRelations

    The default element is an empty list.

    .. document private methods
    .. automethod:: SimpleRelationsLattice._less_equal
    .. automethod:: SimpleRelationsLattice._meet
    .. automethod:: SimpleRelationsLattice._join
    .. automethod:: SimpleRelationsLattice._widening
    """

    def __init__(self, relations: [SimpleRelation] = None):
        super().__init__()
        self.relations = relations if relations is not None else []

    def remove_relations_for_input(self, var: VariableIdentifier, input_id: VariableIdentifier):
        """Removes relations that contain a certain variable from the list and returns a new
        SimpleRelationsLattice element with those relations.
        The variable is in the relations are substituted with the input id

        :param var: relationships that contain that variable are removed from the list
        :param input_id: every occurence of the variable is substituted with this id
        :return: a new SimpleRelationsLattice object with the relations that contain the given
        variable
        """
        relations = [r for r in self.relations if r.contains(var)]
        if len(relations) > 0:
            self.relations[:] = [r for r in self.relations if not r.contains(var)]
        for relation in relations:
            input_id_simple_expr = SimpleExpression.from_expression(input_id)
            relation.substitute(var, input_id_simple_expr)
        return SimpleRelationsLattice(relations)

    def substitute_all(self, var, expr: Expression):
        """Substitutes a variable in all relations with the given expression

        :param var: variable that is substituted
        :param expr: expression the variable is substituted with
        """
        new_relations = []
        for relation in self.relations:
            if isinstance(expr, ListDisplay):
                if relation.contains(var):
                    len_var = LengthIdentifier(var)
                    relation.substitute(len_var, SimpleExpression(const=len(expr.items)))
                    new_relations.append(relation)
                else:
                    new_relations.append(relation)
            elif relation.contains(var):
                expr_simple = SimpleExpression.from_expression(expr)
                if expr_simple is None:
                    if not relation.contains(var):
                        new_relations.append(relation)
                    continue
                new_relation = relation.substitute(var, expr_simple)
                new_relations.append(new_relation)
            else:
                new_relations.append(relation)
        self.relations = new_relations

    def add(self, relation: SimpleRelation):
        """Adds a relation to the list of relations.

        :param relation: relation to add
        """
        self.relations.append(relation)

    @copy_docstring(Lattice.top)
    def top(self):
        self.relations = []

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return len(self.relations) == 0

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'SimpleRelationsLattice') -> bool:
        if len(self.relations) != len(other.relations):
            return len(self.relations) < len(other.relations)
        for relation in self.relations:
            if relation not in other.relations:
                return False
        return True

    @copy_docstring(Lattice._join)
    def _join(self, other: 'SimpleRelationsLattice') -> 'SimpleRelationsLattice':
        new_relations = []
        for relation in self.relations:
            if relation in other.relations:
                new_relations.append(relation)
        self.relations = new_relations
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'SimpleRelationsLattice'):
        raise NotImplementedError

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'SimpleRelationsLattice'):
        raise NotImplementedError

    def __repr__(self):
        return self.relations.__repr__()


class SimpleExpression:
    """
    The SimpleExpression consists of three elements:
    var_pos: if the variable is positive or not
    var: the variable that is used in the expression
    const: a constant used by the expression

    The expression is of the from +/- var + const
    """

    def __init__(self, var_pos=True, var: VariableIdentifier=None, const: float=0):
        super().__init__()
        self.var_pos = var_pos
        self.var = var if var is not None else self.var_zero
        self.const = const

    @classmethod
    def from_expression(cls, expr: Expression):
        inverted = False
        if isinstance(expr, UnaryArithmeticOperation):
            if expr.operator == UnaryArithmeticOperation.Operator.Sub:
                inverted = True
                expr = expr.expression
        if isinstance(expr, Literal):
            val = cls.literal_to_primitive_type(expr)
            if inverted:
                val = -val
            return cls(const=val)
        elif isinstance(expr, (VariableIdentifier, LengthIdentifier)):
            return cls(not inverted, expr)
        elif isinstance(expr, BinaryArithmeticOperation):
            if isinstance(expr.left, VariableIdentifier) and isinstance(expr.right, Literal):
                val = cls.literal_to_primitive_type(expr.right)
                if expr.operator == BinaryArithmeticOperation.Operator.Sub and not inverted:
                    val = -val
                elif expr.operator == BinaryArithmeticOperation.Operator.Add and inverted:
                    val = -val
                return cls(not inverted, expr.left, val)
            elif isinstance(expr.left, Literal) and isinstance(expr.right, VariableIdentifier):
                val = cls.literal_to_primitive_type(expr.left)
                if inverted:
                    val = -val
                var_pos = expr.operator == BinaryArithmeticOperation.Operator.Add and not inverted
                var_pos |= expr.operator == BinaryArithmeticOperation.Operator.Sub and inverted
                return cls(var_pos, expr.right, val)
        return None

    @staticmethod
    def literal_to_primitive_type(lit: Literal):
        """Converts a literal to a primitive type value

        :param lit: literal to convert
        :return: primitive type value of the literal
        """
        if isinstance(lit.typ, IntegerLyraType):
            return int(lit.val)
        elif isinstance(lit.typ, FloatLyraType):
            return float(lit.val)
        elif isinstance(lit.typ, BooleanLyraType):
            return bool(lit.val)
        raise NotImplementedError(f"Convertion for type {lit.typ} is not yet implemented.")

    @property
    def var_zero(self) -> VariableIdentifier:
        return VariableIdentifier(FloatLyraType(), ".VAR0")

    def substitute_expr(self, var: VariableIdentifier, expr: 'SimpleExpression'):
        """Substitutes the variable of the expression with a new expression if the variable is
        present

        :param var: variable to substitute
        :param expr: expression the variable is substituted with
        """
        if self.var != var:
            return
        self.var = expr.var
        self.const += expr.const

    def sub(self, other):
        """Decreases the current expression by the amount given by the other expression.
        Returns None if subtraction is not possible (if the resulting expression is not of the
        form +/- var + const

        :param other: a primitive type or a SimpleExpression that is substracted
        :return: the new SimpleExpression or None if subtraction is not possible
        """
        if isinstance(other, (int, float)):
            self.const -= other
            return self
        if isinstance(other, SimpleExpression):
            if self.var == other.var and other.var_pos:
                self.var = self.var_zero
                self.const -= other.const
            elif self.is_constant():
                self.var_pos = False
                self.var = other.var
                self.const -= other.const
            elif other.is_constant():
                self.const -= other.const
            else:
                return None
            return self
        raise NotImplementedError(f"Substraction for {self} - {other} is not implemented.")

    def is_constant(self):
        return self.var == self.var_zero

    def __hash__(self):
        return hash((self.var_pos, self.var, self.const))

    def __eq__(self, other: 'SimpleExpression'):
        same_var_pos = self.var_pos == other.var_pos
        same_var = self.var == other.var
        same_const = self.const == other.const
        return same_var_pos and same_var and same_const

    def __lt__(self, other: 'SimpleExpression'):
        if self.var_pos != other.var_pos or self.var != other.var:
            return False
        return self.const < other.const

    def __repr__(self):
        if self.var == self.var_zero:
            return f"{self.const.__repr__()}"
        var_sign = "" if self.var_pos else "-"
        if self.const < 0:
            return f"({var_sign}{self.var} - {-self.const})"
        return f"({var_sign}{self.var} + {self.const})"
