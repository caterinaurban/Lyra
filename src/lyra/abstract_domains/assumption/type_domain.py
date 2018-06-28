"""
Type Abstract Domain
====================

Non-relational abstract domain to be used for **input data assumption analysis**.
The set of possible values of a program variable in a state is represented as a type.

:Authors: Caterina Urban and Madelin Schumacher
"""
from collections import defaultdict
from copy import deepcopy
from enum import IntEnum
from typing import List

from lyra.abstract_domains.assumption.assumption_domain import InputMixin
from lyra.abstract_domains.lattice import BottomMixin, ArithmeticMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, ExpressionVisitor, Literal, \
    Input, ListDisplay, Range, AttributeReference, Subscription, Slicing, \
    UnaryArithmeticOperation, BinaryArithmeticOperation
from lyra.core.types import LyraType, BooleanLyraType, IntegerLyraType, FloatLyraType, \
    StringLyraType
from lyra.core.utils import copy_docstring


class TypeLattice(BottomMixin, ArithmeticMixin):
    """Type Lattice::

        String
          |
        Float
          |
        Integer
          |
        Boolean
          |
          ⊥

    The default lattice element is ``String``.

    Let S be the set of all possible strings. We define F ⊆ S, I ⊆ F, B ⊆ I to be the sets of
    all possible strings that can be interpreted as floating-point numbers
    (i.e., F = { 2.35, ..., 9.345, ...}), integers (i.e., I = { -3, ..., 15, ...}),
    and booleans (i.e., B = { 0, 1 }), respectively.
    The concretization function Ɣ: TypeLattice -> 𝒫(S) is defined as follows::

        Ɣ(String) = S
        Ɣ(Float) = F
        Ɣ(Integer) = I
        Ɣ(Boolean) = B
        Ɣ(⊥) = ∅

    .. note::
        One might want to have Ɣ(Boolean) = { 'True', 'False' }. This, however, would yield
        the following different lattice structure::

                   String
                 /        \\
                /        Float
            Boolean        |
                 \\      Integer
                  \\      /
                      ⊥

        which is not compatible with subtyping between boolean and integer types in Python.

    .. document private methods
    .. automethod:: TypeLattice._less_equal
    .. automethod:: TypeLattice._meet
    .. automethod:: TypeLattice._join
    .. automethod:: TypeLattice._widening
    """
    class Status(IntEnum):
        """Type status.

        The current lattice element can be:

        * ``String``: String type

        * ``Float``: Float type

        * ``Integer`` Integer type

        * ``Boolean``: Boolean type
        """
        String = 3
        Float = 2
        Integer = 1
        Boolean = 0

    def __init__(self, type_status: Status = Status.String):
        super().__init__()
        self._element = type_status

    @classmethod
    def from_lyra_type(cls, lyra_type: LyraType):
        if isinstance(lyra_type, BooleanLyraType):
            return cls(TypeLattice.Status.Boolean)
        elif isinstance(lyra_type, IntegerLyraType):
            return cls(TypeLattice.Status.Integer)
        elif isinstance(lyra_type, FloatLyraType):
            return cls(TypeLattice.Status.Float)
        return cls(TypeLattice.Status.String)

    @property
    def element(self):
        """Current lattice element.

        :return: the current lattice element if the type is not bottom, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        return self._element

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return self.element.name

    def boolean(self) -> 'TypeLattice':
        """Integer lattice element.

        :return: current lattice element modified to be the boolean lattice element

        The integer lattice element is ``Boolean``
        """
        return self.replace(TypeLattice(TypeLattice.Status.Boolean))

    def integer(self) -> 'TypeLattice':
        """Integer lattice element.

        :return: current lattice element modified to be the integer lattice element

        The integer lattice element is ``Integer``
        """
        return self.replace(TypeLattice(TypeLattice.Status.Integer))

    def float(self) -> 'TypeLattice':
        """Float lattice element.

        :return: current lattice element modified to be the float lattice element

        The float lattice element is ``Float``.
        """
        return self.replace(TypeLattice(TypeLattice.Status.Float))

    @copy_docstring(BottomMixin.top)
    def top(self) -> 'TypeLattice':
        """The top lattice element is ``String``."""
        return self.replace(TypeLattice())

    def is_boolean(self) -> bool:
        """Test whether the lattice element is boolean.

        :return: whether the lattice element is ``Boolean``
        """
        return self.element == TypeLattice.Status.Boolean

    def is_integer(self) -> bool:
        """Test whether the lattice element is integer.

        :return: whether the lattice element is ``Integer``
        """
        return self.element == TypeLattice.Status.Integer

    def is_float(self) -> bool:
        """Test whether the lattice element is float.

        :return: whether the lattice element is ``Float``
        """
        return self.element == TypeLattice.Status.Float

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        return self.element == TypeLattice.Status.String

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'TypeLattice') -> bool:
        return self.element <= other.element

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'TypeLattice') -> 'TypeLattice':
        return self.replace(TypeLattice(max(self.element, other.element)))

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'TypeLattice'):
        return self.replace(TypeLattice(min(self.element, other.element)))

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'TypeLattice'):
        return self._join(other)

    # arithmetic operations

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'TypeLattice':
        """
        - Boolean = Integer
        - Integer = Integer
        - Float = Float
        - String = ⊥
        """
        if self.is_boolean():
            return self.replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top():
            return self.bottom()
        return self   # nothing to be done

    @copy_docstring(ArithmeticMixin._add)
    def _add(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean + Boolean = Integer
        Boolean + Integer = Integer
        Boolean + Float = Float
        Boolean + String = ⊥
        Integer + Boolean = Integer
        Integer + Integer = Integer
        Integer + Float = Float
        Integer + String = ⊥
        Float + Boolean = Float
        Float + Integer = Float
        Float + Float = Float
        Float + String = ⊥
        String + Boolean = ⊥
        String + Integer = ⊥
        String + Float = ⊥
        String + String = String
        """
        if self.is_boolean() and other.is_boolean():
            return self.replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top() and other.is_top():
            return self
        elif self.is_top() or other.is_top():
            return self.bottom()
        return self.replace(TypeLattice(max(self.element, other.element)))

    @copy_docstring(ArithmeticMixin._sub)
    def _sub(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean - Boolean = Integer
        Boolean - Integer = Integer
        Boolean - Float = Float
        Boolean - String = ⊥
        Integer - Boolean = Integer
        Integer - Integer = Integer
        Integer - Float = Float
        Integer - String = ⊥
        Float - Boolean = Float
        Float - Integer = Float
        Float - Float = Float
        Float - String = ⊥
        String - Boolean = ⊥
        String - Integer = ⊥
        String - Float = ⊥
        String - String = ⊥
        """
        if self.is_boolean() and other.is_boolean():
            return self.replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top() or other.is_top():
            return self.bottom()
        return self.replace(TypeLattice(max(self.element, other.element)))

    @copy_docstring(ArithmeticMixin._mult)
    def _mult(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean * Boolean = Integer
        Boolean * Integer = Integer
        Boolean * Float = Float
        Boolean * String = String
        Integer * Boolean = Integer
        Integer * Integer = Integer
        Integer * Float = Float
        Integer * String = String
        Float * Boolean = Float
        Float * Integer = Float
        Float * Float = Float
        Float * String = ⊥
        String * Boolean = String
        String * Integer = String
        String * Float = ⊥
        String * String = ⊥
        """
        if self.is_boolean() and other.is_boolean():
            return self.replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top() and (other.is_float() or other.is_top()):
            return self.bottom()
        elif other.is_top() and (self.is_float() or self.is_top()):
            return self.bottom()
        return self.replace(TypeLattice(max(self.element, other.element)))


class TypeState(Store, InputMixin):
    """Type assumption analysis state. An element of the type assumption abstract domain.

    Map from each program variable to the type representing its value.
    The value of all program variables is represented by their Lyra type by default.

    .. note::
        This means that, for any map m: VariableIdentifier -> TypeLattice and variable x,
        we should always have m(x) ≤ TypeLattice.from_lyra_type(x.typ)

    When reading input data, the corresponding type assumptions
    are stored in the class member ``inputs``, which is a map
    from each program point to the list of type assumptions on the inputs read at that point.

    .. document private methods
    .. automethod:: TypeState._assume
    .. automethod:: TypeState._substitute
    """
    def __init__(self, variables: List[VariableIdentifier]):
        """Map each program variable to the type representing its value.

        :param variables: list of program variables
        """
        lattices = defaultdict(lambda: TypeLattice)
        arguments = defaultdict(lambda: {'type_status': TypeLattice.Status.String})
        arguments[BooleanLyraType] = {'type_status': TypeLattice.Status.Boolean}
        arguments[IntegerLyraType] = {'type_status': TypeLattice.Status.Integer}
        arguments[FloatLyraType] = {'type_status': TypeLattice.Status.Float}
        super().__init__(variables, lattices, arguments)

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression) -> 'TypeState':
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'TypeState':
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State.output)
    def _output(self, output: Expression) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'TypeState':
        if isinstance(left, VariableIdentifier):
            if isinstance(left.typ, BooleanLyraType):
                # record the current value of the substituted variable
                value: TypeLattice = deepcopy(self.store[left])
                # forget the current value of the substituted variable
                self.store[left].boolean()
                # evaluate the right-hand side bottom-up using the updated store and the Lyra types
                evaluation = self._evaluation.visit(right, self, dict())
                # restrict the value of the right-hand side using that of the substituted variable
                refinement = evaluation[right].meet(value)
                # refine the updated store proceeding top-down on the right-hand side
                self._refinement.visit(right, evaluation, refinement, self)
            elif isinstance(left.typ, IntegerLyraType):
                # record the current value of the substituted variable
                value: TypeLattice = deepcopy(self.store[left])
                # forget the current value of the substituted variable
                self.store[left].integer()
                # evaluate the right-hand side bottom-up using the updated store and the Lyra types
                evaluation = self._evaluation.visit(right, self, dict())
                # restrict the value of the right-hand side using that of the substituted variable
                refinement = evaluation[right].meet(value)
                # refine the updated store proceeding top-down on the right-hand side
                self._refinement.visit(right, evaluation, refinement, self)
            elif isinstance(left.typ, FloatLyraType):
                # record the current value of the substituted variable
                value: TypeLattice = deepcopy(self.store[left])
                # forget the current value of the substituted variable
                self.store[left].float()
                # evaluate the right-hand side bottom-up using the updated store and the Lyra types
                evaluation = self._evaluation.visit(right, self, dict())
                # restrict the value of the right-hand side using that of the substituted variable
                refinement = evaluation[right].meet(value)
                # refine the updated store proceeding top-down on the right-hand side
                self._refinement.visit(right, evaluation, refinement, self)
            elif isinstance(left.typ, StringLyraType):
                # record the current value of the substituted variable
                value: TypeLattice = deepcopy(self.store[left])
                # forget the current value of the substituted variable
                self.store[left].top()
                # evaluate the right-hand side bottom-up using the updated store and the Lyra types
                evaluation = self._evaluation.visit(right, self, dict())
                # restrict the value of the right-hand side using that of the substituted variable
                refinement = evaluation[right].meet(value)
                # refine the updated store proceeding top-down on the right-hand side
                self._refinement.visit(right, evaluation, refinement, self)
            else:
                raise ValueError(f"Variable type {left.typ} is unsupported!")
        else:
            raise NotImplementedError(f"Substitution of {left.__class__.__name__} is unsupported!")
        # check whether the property ∀x. m(x) ≤ TypeLattice.from_lyra_type(x.typ) still holds
        store = self.store
        assert all(store[v].less_equal(TypeLattice.from_lyra_type(v.typ)) for v in store.keys())

        return self

    # expression evaluation

    class ExpressionEvaluation(ExpressionVisitor):
        """Visitor that performs the evaluation of an expression in the type lattice."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            typ = expr.typ
            if isinstance(typ, (BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType)):
                evaluation[expr] = TypeLattice.from_lyra_type(typ)
                return evaluation
            raise ValueError(f"Literal type {typ} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            typ = expr.typ
            if isinstance(typ, (BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType)):
                evaluation[expr] = TypeLattice.from_lyra_type(typ)
                return evaluation
            raise ValueError(f"Input type {expr.typ} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            typ = expr.typ
            if isinstance(typ, (BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType)):
                value: TypeLattice = deepcopy(state.store[expr])
                evaluation[expr] = value.meet(TypeLattice.from_lyra_type(typ))
                return evaluation
            raise ValueError(f"Variable type {typ} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                # same as for UnaryArithmeticOperation.Operator.Sub
                # + Boolean = Integer
                # + Integer = Integer
                # + Float = Float
                # + String = ⊥
                value: TypeLattice = deepcopy(evaluated[expr.expression]).neg()
                evaluated[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                value: TypeLattice = deepcopy(evaluated[expr.expression]).neg()
                evaluated[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated
            raise ValueError(f"Unary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).add(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).sub(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).mult(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            raise ValueError(f"Binary operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances

    class ArithmeticExpressionRefinement(ExpressionVisitor):
        """Visitor that:

        (1) refines the value of an evaluated arithmetic expression based on a given interval; and
        (2) modifies the current state based on the refined value of the arithmetic expression.
        """
        def visit(self, expr: Expression, *args, **kwargs):
            """Visit of an evaluated expression."""
            method = 'visit_' + expr.__class__.__name__
            if hasattr(self, method):
                return getattr(self, method)(expr, *args, **kwargs)
            raise NotImplementedError(
                f"Missing visitor for {expr.__class__.__name__} in {self.__class__.__qualname__}!")

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, evaluation=None, value=None, state=None):
            return state    # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            state.record(value)
            return state    # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, evaluation=None, value=None, state=None):
            typ = expr.typ
            if isinstance(typ, (BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType)):
                state.store[expr] = evaluation[expr].meet(value)
                return state
            raise ValueError(f"Variable type {expr.typ} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            add = UnaryArithmeticOperation.Operator.Add
            sub = UnaryArithmeticOperation.Operator.Sub
            if expr.operator == add or expr.operator == sub:
                refined = evaluation[expr].meet(value)
                val = TypeLattice(TypeLattice.Status.Integer).meet(refined)
                return self.visit(expr.expression, evaluation, val, state)
            raise ValueError(f"Unary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            add = BinaryArithmeticOperation.Operator.Add
            sub = BinaryArithmeticOperation.Operator.Sub
            mult = BinaryArithmeticOperation.Operator.Mult
            if expr.operator == add or expr.operator == sub or expr.operator == mult:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).meet(evaluation[expr.right])
                left = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(refined).meet(evaluation[expr.left])
                right = self.visit(expr.right, evaluation, refinement2, left)
                return right
            raise ValueError(f"Binary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between instances
