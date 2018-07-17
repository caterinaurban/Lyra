"""
Sign Abstract Domain
====================

Non-relational abstract domain to be used for **sign analysis**.
The set of possible values of a program variable is represented as their sign
(negative, zero, positive, ...).

:Author: Jérôme Dohrau and Caterina Urban
"""
from collections import defaultdict
from copy import deepcopy

from lyra.abstract_domains.lattice import ArithmeticMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import *
from lyra.core.types import FloatLyraType

from lyra.core.utils import copy_docstring


class SignLattice(ArithmeticMixin):
    """Sign lattice.

    .. image:: _static/sign.png

    .. document private methods
    .. automethod:: SignLattice._less_equal
    .. automethod:: SignLattice._meet
    .. automethod:: SignLattice._join
    .. automethod:: SignLattice._widening
    .. automethod:: SignLattice._neg
    .. automethod:: SignLattice._add
    .. automethod:: SignLattice._sub
    .. automethod:: SignLattice._mult
    """
    def __init__(self, negative=True, positive=True, zero=True):
        super().__init__()
        self._negative = negative
        self._zero = zero
        self._positive = positive
        
    @property
    def negative(self):
        """Current negative flag.
        
        :return: the current negative flag
        """
        return self._negative
    
    @property
    def zero(self):
        """Current zero flag.
        
        :return: the current zero flag
        """
        return self._zero
    
    @property
    def positive(self):
        """Current positive flag.
        
        :return: the current positive flag
        """
        return self._positive

    def is_negative(self) -> bool:
        """ Indicates whether the element is certainly negative.

        :return: ``True`` if the element is negative.
        """
        return self.negative and not self.positive and not self.zero

    def is_zero(self) -> bool:
        """ Indicates whether the element is certainly zero.

        :return: ``True`` if the element is zero.
        """
        return not self.negative and not self.positive and self.zero

    def is_positive(self) -> bool:
        """ Indicates whether the element is certainly positive.

        :return: ``True`` if the element is positive.
        """
        return not self.negative and self.positive and not self.zero

    def maybe_negative(self) -> bool:
        """ Indicates whether the element may be negative.

        :return: ``True`` if the element may be negative.
        """
        return self.negative

    def maybe_zero(self) -> bool:
        """ Indicates whether the element may be zero.

        :return: ``True`` if the element may be zero.
        """
        return self.zero

    def maybe_positive(self) -> bool:
        """ Indicates whether the element may be positive.

        :return: ``True`` if the element may be positive.
        """
        return self.positive

    def maybe_non_negative(self) -> bool:
        """ Indicates whether the element may be non-negative.

        :return: ``True`` if the element may be non-negative.
        """
        return self.zero or self.positive

    def maybe_non_zero(self) -> bool:
        """ Indicates whether the element may be non-zero.

        :return: ``True`` if the element may be non-zero.
        """
        return self.negative or self.positive

    def maybe_non_positive(self) -> bool:
        """ Indicates whether the element may be non-positive.

        :return: ``True`` if the element may be non-positive.
        """
        return self.negative or self.zero

    def __repr__(self):
        if self.is_top():
            return "⊤"
        elif self.maybe_negative() and self.maybe_zero():
            return "≤0"
        elif self.maybe_zero() and self.maybe_positive():
            return "≥0"
        elif self.maybe_negative() and self.maybe_positive():
            return "≠0"
        elif self.maybe_negative():
            return "<0"
        elif self.maybe_positive():
            return ">0"
        elif self.maybe_zero():
            return "=0"
        else:  # self.is_bottom()
            return "⊥"

    @copy_docstring(ArithmeticMixin.bottom)
    def bottom(self) -> 'SignLattice':
        return self._replace(SignLattice(False, False, False))

    @copy_docstring(ArithmeticMixin.top)
    def top(self) -> 'SignLattice':
        return self._replace(SignLattice(True, True, True))

    @copy_docstring(ArithmeticMixin.is_bottom)
    def is_bottom(self) -> bool:
        return not self.negative and not self.positive and not self.zero

    @copy_docstring(ArithmeticMixin.is_top)
    def is_top(self) -> bool:
        return self.negative and self.positive and self.zero

    @copy_docstring(ArithmeticMixin._less_equal)
    def _less_equal(self, other: 'SignLattice') -> bool:
        negative = not self.maybe_negative() or other.maybe_negative()
        zero = not self.maybe_zero() or other.maybe_zero()
        positive = not self.maybe_positive() or other.maybe_positive()
        return negative and zero and positive

    @copy_docstring(ArithmeticMixin._join)
    def _join(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative() or other.maybe_negative()
        zero = self.maybe_zero() or other.maybe_zero()
        positive = self.maybe_positive() or other.maybe_positive()
        return self._replace(SignLattice(negative, positive, zero))

    @copy_docstring(ArithmeticMixin._meet)
    def _meet(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative() and other.maybe_negative()
        zero = self.maybe_zero() and other.maybe_zero()
        positive = self.maybe_positive() and other.maybe_positive()
        return self._replace(SignLattice(negative, positive, zero))

    @copy_docstring(ArithmeticMixin._widening)
    def _widening(self, other: 'SignLattice') -> 'SignLattice':
        return self._join(other)

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'SignLattice':
        negative = self.maybe_positive()
        zero = self.maybe_zero()
        positive = self.maybe_negative()
        return self._replace(SignLattice(negative, positive, zero))

    def _add(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative() and not other.is_bottom()) or \
                   (self.maybe_non_negative() and other.maybe_negative())
        positive = (self.maybe_positive() and not other.is_bottom()) or \
                   (self.maybe_non_positive() and other.maybe_positive())
        zero = (self.maybe_zero() and other.maybe_zero()) or \
               (self.maybe_negative() and other.maybe_positive()) or \
               (self.maybe_positive() and other.maybe_negative())
        return self._replace(SignLattice(negative, positive, zero))

    def _sub(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative() and not other.is_bottom()) or \
                   (self.maybe_non_negative() and other.maybe_positive())
        positive = (self.maybe_positive() and not other.is_bottom()) or \
                   (self.maybe_non_positive() and other.maybe_negative())
        zero = (self.maybe_zero() and other.maybe_zero()) or \
               (self.maybe_negative() and other.maybe_negative()) or \
               (self.maybe_positive() and other.maybe_positive())
        return self._replace(SignLattice(negative, positive, zero))

    def _mult(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative() and other.maybe_positive()) or \
                   (self.maybe_positive() and other.maybe_negative())
        positive = (self.maybe_negative() and other.maybe_negative()) or \
                   (self.maybe_positive() and other.maybe_positive())
        zero = self.maybe_zero() or other.maybe_zero()
        return self._replace(SignLattice(negative, positive, zero))


class SignState(Store, State):
    """Sign analysis state. An element of the sign abstract domain.

    Map from each program variable to the sign representing its value.

    .. document private methods
    .. automethod:: SignState._assign
    .. automethod:: SignState._assume
    .. automethod:: SignState._output
    .. automethod:: SignState._substitute

    """
    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        """Map each program variable to the sign representing its value.

        :param variables: the list of program variables
        """
        lattices = defaultdict(lambda: SignLattice)
        super().__init__(variables, lattices)
        State.__init__(self, precursory)

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression) -> 'SignState':
        if isinstance(left, VariableIdentifier):
            evaluation = self._evaluation.visit(right, self, dict())
            self.store[left] = evaluation[right]
            return self
        elif isinstance(left, Subscription):
            evaluation = self._evaluation.visit(right, self, dict())
            self.store[left.target].join(evaluation[right])
            return self
        raise NotImplementedError(f"Assignment to {left.__class__.__name__} is unsupported!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'SignState':
        normal = NegationFreeNormalExpression().visit(condition)
        if isinstance(normal, VariableIdentifier) and isinstance(normal.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(normal, self, dict())
            true = SignLattice(False, True, False)
            return self._refinement.visit(normal, evaluation, true, self)
        elif isinstance(normal, UnaryBooleanOperation):
            if normal.operator == UnaryBooleanOperation.Operator.Neg:
                if isinstance(normal.expression, VariableIdentifier):
                    if isinstance(normal.expression.typ, BooleanLyraType):
                        evaluation = self._evaluation.visit(normal, self, dict())
                        false = SignLattice(False, False, True)
                        return self._refinement.visit(normal.expression, evaluation, false, self)
        elif isinstance(normal, BinaryBooleanOperation):
            if normal.operator == BinaryBooleanOperation.Operator.And:
                right = deepcopy(self)._assume(normal.right)
                return self._assume(normal.left).meet(right)
            if normal.operator == BinaryBooleanOperation.Operator.Or:
                right = deepcopy(self)._assume(normal.right)
                return self._assume(normal.left).join(right)
        elif isinstance(normal, BinaryComparisonOperation):
            evaluation = self._evaluation.visit(normal.left, self, dict())
            non_positive = SignLattice(True, False, True)
            return self._refinement.visit(normal.left, evaluation, non_positive, self)
        error = f"Assumption of a {normal.__class__.__name__} expression is unsupported!"
        raise ValueError(error)

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'SignState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'SignState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'SignState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'SignState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'SignState':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'SignState':
        if isinstance(left, VariableIdentifier):
            # record the current value of the substituted variable
            value: SignLattice = deepcopy(self.store[left])
            # forget the current value of the substituted variable
            self.store[left].top()
            # evaluate the right-hand side proceeding bottom-up using the updated store
            evaluation = self._evaluation.visit(right, self, dict())
            # restrict the value of the right-hand side using that of the substituted variable
            refinement = evaluation[right].meet(value)
            # refine the updated store proceeding top-down on the right-hand side
            self._refinement.visit(right, evaluation, refinement, self)
            return self
        raise NotImplementedError(f"Substitution of {left.__class__.__name__} is unsupported!")

    # expression evaluation

    class ExpressionEvaluation(ExpressionVisitor):
        """Visitor that performs the evaluation of an expression in the sign lattice."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                if expr.val == "True":
                    evaluation[expr] = SignLattice(False, True, False)
                else:  # expr.val == "False"
                    evaluation[expr] = SignLattice(False, False, True)
                return evaluation
            elif isinstance(expr.typ, IntegerLyraType):
                value = int(expr.val)
                evaluation[expr] = SignLattice(value < 0, value > 0, value == 0)
                return evaluation
            elif isinstance(expr.typ, FloatLyraType):
                value = float(expr.val)
                evaluation[expr] = SignLattice(value < 0.0, value > 0.0, value == 0.0)
                return evaluation
            evaluation[expr] = SignLattice()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                evaluation[expr] = SignLattice(False, True, True)
                return evaluation
            evaluation[expr] = SignLattice()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            for item in expr.items:
                evaluation = self.visit(item, state, evaluation)
            evaluation[expr] = SignLattice().big_join([evaluation[item] for item in expr.items])
            return evaluation

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
            if expr in evaluation:
                return evaluation  # nothing to be done
            self.visit(expr.target, state, evaluation)
            evaluation[expr] = evaluation[expr.target]
            return evaluation

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
                evaluated[expr] = evaluated[expr.expression]
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                evaluated[expr] = deepcopy(evaluated[expr.expression]).neg()
                return evaluated
            raise ValueError(f"Unary arithmetic operator {expr.operator} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                value = evaluated[expr.expression]
                if value == SignLattice(False, True, True):
                    evaluated[expr] = value
                    return evaluated
                elif value == SignLattice(False, True, False):
                    evaluated[expr] = SignLattice(False, False, True)
                    return evaluated
                elif value == SignLattice(False, False, True):
                    evaluated[expr] = SignLattice(False, True, False)
                    return evaluated
            raise ValueError(f"Unary boolean operator {expr.operator} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation1 = self.visit(expr.left, state, evaluation)
            evaluation2 = self.visit(expr.right, state, evaluation1)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).add(evaluation2[expr.right])
                return evaluation2
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).sub(evaluation2[expr.right])
                return evaluation2
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).mult(evaluation2[expr.right])
                return evaluation2
            raise ValueError(f"Binary arithmetic operator {expr.operator} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluation1 = self.visit(expr.left, state, evaluation)
            evaluation2 = self.visit(expr.right, state, evaluation1)
            if expr.operator == BinaryBooleanOperation.Operator.And:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).mult(evaluation2[expr.right])
                return evaluation2
            elif expr.operator == BinaryBooleanOperation.Operator.Or:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).add(evaluation2[expr.right])
                return evaluation2
            raise ValueError("Binary operator {expr.operator} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self,  expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

    _evaluation = ExpressionEvaluation()  # static class member shared between instances

    # expression refinement

    class ArithmeticExpressionRefinement(ExpressionVisitor):
        """Visitor that:

        (1) refines the value of an evaluated arithmetic expression based on a given sign; and
        (2) modifies the current state based on the refined value of the arithmetic expression.
        """

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, evaluation=None, value=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, evaluation=None, value=None, state=None):
            state.store[expr] = evaluation[expr].meet(value)
            return state

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
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return self.visit(expr.expression, evaluation, value, state)
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                refined = evaluation[expr].meet(value)
                val = refined.neg()
                return self.visit(expr.expression, evaluation, val, state)
            raise ValueError(f"Unary operator {expr.operator} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                if isinstance(expr.expression.typ, BooleanLyraType):
                    refined: SignLattice = evaluation[expr].meet(value)
                    if refined == SignLattice(False, True, True):
                        refinement = SignLattice(False, True, True)
                        return self.visit(expr.expression, evaluation, refinement, state)
                    elif refined == SignLattice(False, True, False):
                        refinement = SignLattice(False, False, True)
                        return self.visit(expr.expression, evaluation, refinement, state)
                    elif refined == SignLattice(False, False, True):
                        refinement = SignLattice(False, True, False)
                        return self.visit(expr.expression, evaluation, refinement, state)
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).sub(evaluation[expr.right])
                left = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(refined).sub(evaluation[expr.left])
                right = self.visit(expr.right, evaluation, refinement2, left)
                return right
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).add(evaluation[expr.right])
                left = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(evaluation[expr.left]).sub(refined)
                right = self.visit(expr.right, evaluation, refinement2, left)
                return right
            raise ValueError(f"Binary operator {expr.operator} is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between instances
