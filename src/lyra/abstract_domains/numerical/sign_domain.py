"""
Sign Abstract Domain
====================

Abstract domain to be used for **sign analysis**. The set of possible values of a program variable
is represented as an element of the sign lattice that keeps track whether the variable may be
negative, positive, or zero.

:Author: Jérôme Dohrau
"""
from collections import defaultdict
from copy import deepcopy

from lyra.abstract_domains.lattice import ArithmeticMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import *
from lyra.core.types import FloatLyraType, ListLyraType

from lyra.core.utils import copy_docstring


class SignLattice(ArithmeticMixin):
    """
    Sign lattice.
    """

    def __init__(self, negative=True, positive=True, zero=True):
        super().__init__()
        self._negative = negative
        self._positive = positive
        self._zero = zero

    @property
    def is_negative(self) -> bool:
        """ Indicates whether the element is certainly negative.

        :return: ``True`` if the element is negative.
        """
        return self._negative and not self._positive and not self._zero

    @property
    def is_positive(self) -> bool:
        """ Indicates whether the element is certainly positive.

        :return: ``True`` if the element is positive.
        """
        return not self._negative and self._positive and not self._zero

    @property
    def is_zero(self) -> bool:
        """ Indicates whether the element is certainly zero.

        :return: ``True`` if the element is zero.
        """
        return not self._negative and not self._positive and self._zero

    @property
    def maybe_negative(self) -> bool:
        """ Indicates whether the element may be negative.

        :return: ``True`` if the element may be negative.
        """
        return self._negative

    @property
    def maybe_positive(self) -> bool:
        """ Indicates whether the element may be positive.

        :return: ``True`` if the element may be positive.
        """
        return self._positive

    @property
    def maybe_zero(self) -> bool:
        """ Indicates whether the element may be zero.

        :return: ``True`` if the element may be zero.
        """
        return self._zero

    @property
    def maybe_non_negative(self) -> bool:
        """ Indicates whether the element may be non-negative.

        :return: ``True`` if the element may be non-negative.
        """
        return self._zero or self._positive

    @property
    def maybe_non_positive(self) -> bool:
        """ Indicates whether the element may be non-positive.

        :return: ``True`` if the element may be non-positive.
        """
        return self._negative or self._zero

    @property
    def maybe_non_zero(self) -> bool:
        """ Indicates whether the element may be non-zero.

        :return: ``True`` if the element may be non-zero.
        """
        return self._negative or self._positive

    def __repr__(self):
        if self.is_top():
            return "⊤"
        elif self.maybe_negative and self.maybe_zero:
            return "≤0"
        elif self.maybe_zero and self.maybe_positive:
            return "≥0"
        elif self.maybe_negative and self.maybe_positive:
            return "≠0"
        elif self.maybe_negative:
            return "<0"
        elif self.maybe_positive:
            return ">0"
        elif self.maybe_zero:
            return "=0"
        else:
            return "⊥"

    @copy_docstring(ArithmeticMixin.bottom)
    def bottom(self) -> 'SignLattice':
        return self.replace(SignLattice(False, False, False))

    @copy_docstring(ArithmeticMixin.top)
    def top(self) -> 'SignLattice':
        return self.replace(SignLattice(True, True, True))

    @copy_docstring(ArithmeticMixin.is_bottom)
    def is_bottom(self) -> bool:
        return not self._negative and not self._positive and not self._zero

    @copy_docstring(ArithmeticMixin.is_top)
    def is_top(self) -> bool:
        return self._negative and self._positive and self._zero

    @copy_docstring(ArithmeticMixin._less_equal)
    def _less_equal(self, other: 'SignLattice') -> bool:
        return (not self.maybe_negative or other.maybe_negative) and \
               (not self.maybe_positive or other.maybe_positive) and \
               (not self.maybe_zero or other.maybe_zero)

    @copy_docstring(ArithmeticMixin._join)
    def _join(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative or other.maybe_negative
        positive = self.maybe_positive or other.maybe_positive
        zero = self.maybe_zero or other.maybe_zero
        return self.replace(SignLattice(negative, positive, zero))

    @copy_docstring(ArithmeticMixin._meet)
    def _meet(self, other: 'SignLattice') -> 'SignLattice':
        negative = self.maybe_negative and other.maybe_negative
        positive = self.maybe_positive and other.maybe_positive
        zero = self.maybe_zero and other.maybe_zero
        return self.replace(SignLattice(negative, positive, zero))

    @copy_docstring(ArithmeticMixin._widening)
    def _widening(self, other: 'SignLattice') -> 'SignLattice':
        return self._join(other)

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'SignLattice':
        negative = self.maybe_positive
        positive = self.maybe_negative
        zero = self.maybe_zero
        return self.replace(SignLattice(negative, positive, zero))

    def _add(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative and not other.is_bottom()) or \
                   (self.maybe_non_negative and other.maybe_negative)
        positive = (self.maybe_positive and not other.is_bottom()) or \
                   (self.maybe_non_positive and other.maybe_positive)
        zero = (self.maybe_zero and other.maybe_zero) or \
               (self.maybe_negative and other.maybe_positive) or \
               (self.maybe_positive and other.maybe_negative)
        return self.replace(SignLattice(negative, positive, zero))

    def _sub(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative and not other.is_bottom()) or \
                   (self.maybe_non_negative and other.maybe_positive)
        positive = (self.maybe_positive and not other.is_bottom()) or \
                   (self.maybe_non_positive and other.maybe_negative)
        zero = (self.maybe_zero and other.maybe_zero) or \
               (self.maybe_negative and other.maybe_negative) or \
               (self.maybe_positive and other.maybe_positive)
        return self.replace(SignLattice(negative, positive, zero))

    def _mult(self, other: 'SignLattice') -> 'SignLattice':
        negative = (self.maybe_negative and other.maybe_positive) or \
                   (self.maybe_positive and other.maybe_negative)
        positive = (self.maybe_negative and other.maybe_negative) or \
                   (self.maybe_positive and other.maybe_positive)
        zero = self.maybe_zero or other.maybe_zero
        return self.replace(SignLattice(negative, positive, zero))


class SignState(Store, State):
    def __init__(self, variables: List[VariableIdentifier]):
        """ Map each program variable to the sign lattice element representing its value.

        :param variables: the list of program variables
        """
        lattices = defaultdict(lambda: SignLattice)
        super().__init__(variables, lattices)

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression) -> 'SignState':
        if isinstance(left, VariableIdentifier):
            evaluation = self._evaluation.visit(right, self, dict())
            self.store[left] = evaluation[right]
            return self
        if isinstance(left, Subscription):
            evaluation = self._evaluation.visit(right, self, dict())
            self.store[left.target].join(evaluation[right])
            return self
        raise NotImplementedError(f"Assignment to {left.__class__.__name__} is not supported!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'SignState':
        negation_free_normal_expr = NegationFreeNormalExpression()
        converted = negation_free_normal_expr.preprocess(condition)
        normal = negation_free_normal_expr.visit(converted)
        if isinstance(normal, VariableIdentifier) and isinstance(normal.typ, BooleanLyraType):
            evaluation = self._evaluation.visit(normal, self, dict())
            true = SignLattice(False, True, False)
            return self._refinement.visit(normal, evaluation, true, self)
        elif isinstance(normal, UnaryBooleanOperation):
            if normal.operator == UnaryBooleanOperation.Operator.Neg:
                if isinstance(normal.expression, VariableIdentifier) and \
                        isinstance(normal.expression.typ, BooleanLyraType):
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
        error = f"Assumption of a {normal.__class__.__name__} expression is not supported!"
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

    @copy_docstring(State.raise_error)
    def raise_error(self) -> 'SignState':
        return self

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'SignState':
        error = f"Substitution for {left} is not yet implemented!"
        raise NotImplementedError(error)

    class ExpressionEvaluation(ExpressionVisitor):
        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: 'Literal', state: 'SignState' = None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                if expr.val == "True":
                    evaluation[expr] = SignLattice(False, True, False)
                else:  # expr.val == "False"
                    evaluation[expr] = SignLattice(False, False, True)
                return evaluation
            if isinstance(expr.typ, IntegerLyraType):
                value = int(expr.val)
                evaluation[expr] = SignLattice(value < 0, value > 0, value == 0)
                return evaluation
            if isinstance(expr.typ, FloatLyraType):
                value = float(expr.val)
                evaluation[expr] = SignLattice(value < 0.0, value > 0.0, value == 0.0)
                return evaluation
            # return top by default
            evaluation[expr] = SignLattice()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: 'Input', state: 'SignState' = None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if isinstance(expr.typ, BooleanLyraType):
                evaluation[expr] = SignLattice(False, True, True)
                return evaluation
            if isinstance(expr.typ, IntegerLyraType) or isinstance(expr.typ, FloatLyraType):
                evaluation[expr] = SignLattice()
                return evaluation
            # return top by default
            evaluation[expr] = SignLattice()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: 'VariableIdentifier', state: 'SignState' = None,
                                     evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: 'ListDisplay', state: 'SignState' = None,
                              evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            for item in expr.items:
                evaluation = self.visit(item, state, evaluation)
            evaluation[expr] = SignLattice().big_join([evaluation[item] for item in expr.items])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: 'Range', state: 'SignState' = None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: 'AttributeReference', state: 'SignState' = None,
                                     evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: 'Subscription', state: 'SignState' = None,
                               evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            self.visit(expr.target, state, evaluation)
            evaluation[expr] = evaluation[expr.target]
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: 'Slicing', state: 'SignState' = None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation',
                                           state: 'SignState' = None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                evaluated = self.visit(expr.expression, state, evaluation)
                evaluated[expr] = evaluated[expr.expression]
                return evaluated
            if expr.operator == UnaryArithmeticOperation.Operator.Sub:
                evaluated = self.visit(expr.expression, state, evaluation)
                evaluated[expr] = evaluated[expr.expression].neg()
                return evaluated
            raise ValueError(f"Unary operator {expr.operator} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation',
                                        state: 'SignState' = None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                evaluated = self.visit(expr.expression, state, evaluation)
                value = evaluated[expr.expression]
                if value == SignLattice(False, True, True):
                    evaluated[expr] = value
                    return evaluated
                if value == SignLattice(False, True, False):
                    evaluated[expr] = SignLattice(False, False, True)
                    return evaluated
                if value == SignLattice(False, False, True):
                    evaluated[expr] = SignLattice(False, True, False)
                    return evaluated
            raise ValueError(f"Unary operator {expr.operator} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation',
                                            state: 'SignState' = None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation1 = self.visit(expr.left, state, evaluation)
            evaluation2 = self.visit(expr.right, state, evaluation1)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).add(evaluation2[expr.right])
                return evaluation2
            if expr.operator == BinaryArithmeticOperation.Operator.Sub:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).sub(evaluation2[expr.right])
                return evaluation2
            if expr.operator == BinaryArithmeticOperation.Operator.Mult:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).mult(evaluation2[expr.right])
                return evaluation2
            raise ValueError(f"Binary operator {expr.operator} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation',
                                         state: 'SignState' = None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluation1 = self.visit(expr.left, state, evaluation)
            evaluation2 = self.visit(expr.right, state, evaluation1)
            if expr.operator == BinaryBooleanOperation.Operator.And:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).mult(evaluation2[expr.right])
                return evaluation2
            if expr.operator == BinaryBooleanOperation.Operator.Or:
                evaluation2[expr] = deepcopy(evaluation2[expr.left]).add(evaluation2[expr.right])
                return evaluation2
            raise ValueError("Binary operator {expr.operator} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation',
                                            state: 'SignState' = None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

    _evaluation = ExpressionEvaluation()  # static class member shared between instances

    class ArithmeticExpressionRefinement(ExpressionVisitor):
        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: 'Literal', evaluation=None, value: 'SignLattice' = None,
                          state: 'SignState' = None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: 'Input', evaluation=None, value: 'SignLattice' = None,
                        state: 'SignState' = None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: 'VariableIdentifier', evaluation=None,
                                     value: 'SignLattice' = None, state: 'SignState' = None):
            state.store[expr] = evaluation[expr].meet(value)
            return state

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: 'ListDisplay', evaluation=None,
                              value: 'SignLattice' = None, state: 'SignState' = None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: 'Range', evaluation=None, value: 'SignLattice' = None,
                        state: 'SignState' = None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: 'AttributeReference', evaluation=None,
                                     value: 'SignLattice' = None, state: 'SignState' = None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: 'Subscription', evaluation=None,
                               value: 'SignLattice' = None, state: 'SignState' = None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: 'Slicing', evaluation=None, value: 'SignLattice' = None,
                          state: 'SignState' = None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation', evaluation=None,
                                           value: 'SignLattice' = None, state: 'SignState' = None):
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return self.visit(expr.expression, evaluation, value, state)
            if expr.operator == UnaryArithmeticOperation.Operator.Sub:
                negated_refined_value = evaluation[expr].meet(value).neg()
                return self.visit(expr.expression, evaluation, negated_refined_value, state)
            raise ValueError(f"Unary operator {expr.operator} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', evaluation=None,
                                        value: 'SignLattice' = None, state: 'SignState' = None):
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                refined_value: SignLattice = evaluation[expr].meet(value)
                if refined_value == SignLattice(False, True, True):
                    return self.visit(expr.expression, evaluation, refined_value, state)
                if refined_value == SignLattice(False, True, False):
                    negated_refined_value = SignLattice(False, False, True)
                    return self.visit(expr.expression, evaluation, negated_refined_value, state)
                if refined_value == SignLattice(False, False, True):
                    negated_refined_value = SignLattice(False, True, False)
                    return self.visit(expr.expression, evaluation, negated_refined_value, state)
            error = f"Refinement for a {expr.__class__.__name__} expression is not supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation',
                                            evaluation=None, value: 'SignLattice' = None,
                                            state: 'SignState' = None):
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                refined_value = evaluation[expr].meet(value)
                left_value = deepcopy(refined_value).sub(evaluation[expr.right])
                left_state = self.visit(expr.left, evaluation, left_value, state)
                right_value = deepcopy(refined_value).sub(evaluation[expr.left])
                right_state = self.visit(expr.right, evaluation, right_value, left_state)
                return right_state
            if expr.operator == BinaryArithmeticOperation.Operator.Sub:
                refined_value = evaluation[expr].meet(value)
                left_value = deepcopy(refined_value).add(evaluation[expr.right])
                left_state = self.visit(expr.left, evaluation, left_value, state)
                right_value = deepcopy(evaluation[expr.left]).sub(refined_value)
                right_state = self.visit(expr.right, evaluation, right_value, left_state)
                return right_state
            raise ValueError(f"Binary operator {expr.operator} is not supported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', evaluation=None,
                                         value: 'SignLattice' = None, state: 'SignState' = None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation',
                                            evaluation=None, value: 'SignLattice' = None,
                                            state: 'SignState' = None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not supported!"
            raise ValueError(error)

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between instances
