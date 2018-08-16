"""
Basis Abstract Domain
=====================

Interface of an abstract domain mapping variables to lattice elements.

:Author: Caterina Urban
"""
from abc import ABCMeta
from collections import defaultdict
from copy import deepcopy
from typing import Set, Dict, Type, Any

from lyra.abstract_domains.lattice import Lattice, ArithmeticMixin, BooleanMixin, SequenceMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, Slicing, \
    BinaryBooleanOperation, ExpressionVisitor, Literal, LengthIdentifier, ListDisplay, \
    AttributeReference, Input, Range, UnaryArithmeticOperation, BinaryArithmeticOperation, \
    UnaryBooleanOperation, TupleDisplay, SetDisplay, DictDisplay, BinarySequenceOperation
from lyra.core.types import LyraType, BooleanLyraType, SequenceLyraType
from lyra.core.utils import copy_docstring


class Basis(Store, State, metaclass=ABCMeta):
    """Analysis basic state. A mutable element of a basis abstract domain.

    .. warning::
        Lattice operations and statements modify the current state.
    """
    def __init__(self, variables: Set[VariableIdentifier], lattices: Dict[LyraType, Type[Lattice]],
                 arguments: Dict[LyraType, Dict[str, Any]] = defaultdict(lambda: dict()),
                 precursory: State = None):
        super().__init__(variables, lattices, arguments)
        State.__init__(self, precursory)

    @copy_docstring(State.is_bottom)
    def is_bottom(self) -> bool:
        """The current state is bottom if `any` non-summary variable maps to a bottom element,
        or if the length identifier of `any` summary variable maps to a bottom element."""
        for variable, element in self.store.items():
            if isinstance(variable.typ, (SequenceLyraType)):
                if element.is_bottom() and self.store[LengthIdentifier(variable)].is_bottom():
                    return True
            elif element.is_bottom():
                return True
        return False

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression) -> 'Basis':
        if isinstance(left, VariableIdentifier):
            evaluation = self._evaluation.visit(right, self, dict())
            self.store[left] = evaluation[right]
            return self
        elif isinstance(left, Subscription) or isinstance(left, Slicing):
            # copy the current state
            current: Basis = deepcopy(self)
            # perform the assignment on the copy of the current state
            evaluation = self._evaluation.visit(right, self, dict())
            self.store[left.target] = evaluation[right]
            # perform a weak update on the current state
            return self.join(current)
        raise NotImplementedError(f"Assignment to {left.__class__.__name__} is unsupported!")

    def _assume_binarybooleanoperation(self, condition: BinaryBooleanOperation) -> 'Basis':
        """Assume that some binary boolean condition holds in the current state.

        :param condition: expression representing the assumed binary boolean condition
        :return: current state modified to satisfy the assumption

        """
        if condition.operator == BinaryBooleanOperation.Operator.And:
            right = deepcopy(self)._assume(condition.right)
            return self._assume(condition.left).meet(right)
        if condition.operator == BinaryBooleanOperation.Operator.Or:
            right = deepcopy(self)._assume(condition.right)
            return self._assume(condition.left).join(right)
        error = f"Assumption of a boolean condition with {condition.operator} is unsupported!"
        raise ValueError(error)

    @copy_docstring(State.enter_if)
    def enter_if(self):
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self):
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self):
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self):
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'Basis':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression):
        if isinstance(left, VariableIdentifier):
            # record the current value of the substituted variable
            value: Basis = deepcopy(self.store[left])
            # forget the current value of the substituted variable
            self.store[left].top()
            # evaluate the right-hand side proceeding bottom-up using the updated store
            evaluation = self._evaluation.visit(right, self, dict())
            # restrict the value of the right-hand side using that of the substituted variable
            refinement = evaluation[right].meet(value)
            # refine the updated store proceeding top-down on the right-hand side
            self._refinement.visit(right, evaluation, refinement, self)
            return self
        elif isinstance(left, Subscription) or isinstance(left, Slicing):
            # copy the current state
            current: Basis = deepcopy(self)
            # perform the substitution on the copy of the current state
            target = left.target
            value: Basis = deepcopy(current.store[target])
            current.store[target].top()
            evaluation = current._evaluation.visit(right, current, dict())
            refinement = evaluation[right].meet(value)
            current._refinement.visit(right, evaluation, refinement, current)
            # perform a weak update on the current state
            return self.join(current)
        raise NotImplementedError(f"Substitution of {left.__class__.__name__} is unsupported!")

    # expression evaluation

    class ExpressionEvaluation(ExpressionVisitor):
        """Visitor that performs the evaluation of an expression in the lattice."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr: LengthIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation   # nothing to be done
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                value = value.join(evaluated[item])
            evaluation[expr] = value
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                value = value.join(evaluated[item])
            evaluation[expr] = value
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                value = value.join(evaluated[item])
            evaluation[expr] = value
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for key in expr.keys:
                evaluated = self.visit(key, state, evaluated)
                value = value.join(evaluated[key])
            for val in expr.values:
                evaluated = self.visit(val, state, evaluated)
                value = value.join(evaluated[val])
            evaluation[expr] = value
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target, state, evaluation)
            evaluation[expr] = evaluated[expr.target]
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target, state, evaluation)
            evaluation[expr] = evaluated[expr.target]
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            value = state.lattices[expr.typ](**state.arguments[expr.typ])
            if isinstance(expr.typ, BooleanLyraType) and isinstance(value, BooleanMixin):
                evaluation[expr] = value.maybe()
            else:
                evaluation[expr] = value.top()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            value = evaluated[expr.expression]
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                evaluated[expr] = value
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                if isinstance(value, ArithmeticMixin):
                    evaluated[expr] = deepcopy(value).neg()
                else:
                    evaluated[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated
            raise ValueError(f"Unary arithmetic operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            value = evaluated[expr.expression]
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                if isinstance(value, BooleanMixin):
                    evaluated[expr] = deepcopy(value).compl()
                else:
                    evaluated[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated
            raise ValueError(f"Unary boolean operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            value1 = evaluated2[expr.left]
            value2 = evaluated2[expr.right]
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                if isinstance(value1, ArithmeticMixin):
                    evaluated2[expr] = deepcopy(value1).add(value2)
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                if isinstance(value1, ArithmeticMixin):
                    evaluated2[expr] = deepcopy(value1).sub(value2)
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                if isinstance(value1, ArithmeticMixin):
                    evaluated2[expr] = deepcopy(value1).mult(value2)
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Div:
                if isinstance(value1, ArithmeticMixin):
                    evaluated2[expr] = deepcopy(value1).div(value2)
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated2
            raise ValueError(f"Binary arithmetic operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
        def visit_BinarySequenceOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            value1 = evaluated2[expr.left]
            value2 = evaluated2[expr.right]
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                if isinstance(value1, SequenceMixin):
                    evaluated2[expr] = deepcopy(value1).concat(value2)
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated2
            raise ValueError(f"Binary sequence operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            value1 = evaluated2[expr.left]
            value2 = evaluated2[expr.right]
            if expr.operator == BinaryBooleanOperation.Operator.And:
                if isinstance(value1, BooleanMixin):
                    evaluated2[expr] = deepcopy(value1).conj(value2)
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated2
            elif expr.operator == BinaryBooleanOperation.Operator.Or:
                if isinstance(value1, BooleanMixin):
                    evaluated2[expr] = deepcopy(value1).disj(value2)
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                return evaluated2
            raise ValueError(f"Binary arithmetic operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances

    # expression refinement

    class ExpressionRefinement(ExpressionVisitor):
        """Visitor that:

        (1) refines the value of an evaluated expression based on a given lattice element; and
        (2) modifies the current state based on the refined value of the expression.
        """

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, evaluation=None, value=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            state.store[expr] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            state.store[expr] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            updated = state
            for item in expr.items:
                updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            updated = state
            for item in expr.items:
                updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            updated = state
            for item in expr.items:
                updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            updated = state
            for key in expr.keys:
                updated = self.visit(key, evaluation, refined, updated)
            for val in expr.values:
                updated = self.visit(val, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, evaluation=None, value=None, state=None):
            refined = evaluation[expr]      # weak update
            state.store[expr.target] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, evaluation=None, value=None, state=None):
            refined = evaluation[expr]      # weak update
            state.store[expr.target] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                return self.visit(expr.expression, evaluation, value, state)
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                refined = evaluation[expr].meet(value)
                if isinstance(refined, ArithmeticMixin):
                    refinement = deepcopy(refined).neg()
                else:
                    refinement = deepcopy(refined).top()
                return self.visit(expr.expression, evaluation, refinement, state)
            raise ValueError(f"Unary arithmetic operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == UnaryBooleanOperation.Operator.Neg:
                refined = evaluation[expr].meet(value)
                if isinstance(refined, BooleanMixin):
                    if refined.is_false():
                        refinement = deepcopy(refined).true()
                    elif refined.is_true():
                        refinement = deepcopy(refined).false()
                    else:
                        assert refined.is_maybe()
                        refinement = deepcopy(refined)
                else:
                    refinement = deepcopy(refined).top()
                return self.visit(expr.expression, evaluation, refinement, state)
            raise ValueError(f"Unary boolean operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                refined = evaluation[expr].meet(value)
                if isinstance(refined, ArithmeticMixin):
                    refinement1 = deepcopy(refined).sub(evaluation[expr.right])
                else:
                    refinement1 = deepcopy(refined).top()
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
                if isinstance(refined, ArithmeticMixin):
                    refinement2 = deepcopy(refined).sub(evaluation[expr.left])
                else:
                    refinement2 = deepcopy(refined).top()
                updated2 = self.visit(expr.right, evaluation, refinement2, updated1)
                return updated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                refined = evaluation[expr].meet(value)
                if isinstance(refined, ArithmeticMixin):
                    refinement1 = deepcopy(refined).add(evaluation[expr.right])
                else:
                    refinement1 = deepcopy(refined).top()
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
                if isinstance(refined, ArithmeticMixin):
                    refinement2 = deepcopy(evaluation[expr.left]).sub(refined)
                else:
                    refinement2 = deepcopy(refined).top()
                updated2 = self.visit(expr.right, evaluation, refinement2, updated1)
                return updated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                refined = evaluation[expr].meet(value)
                if isinstance(refined, ArithmeticMixin):
                    refinement1 = deepcopy(refined).div(evaluation[expr.right])
                else:
                    refinement1 = deepcopy(refined).top()
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
                if isinstance(refined, ArithmeticMixin):
                    refinement2 = deepcopy(refined).div(evaluation[expr.left])
                else:
                    refinement2 = deepcopy(refined).top()
                updated2 = self.visit(expr.right, evaluation, refinement2, updated1)
                return updated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Div:
                refined = evaluation[expr].meet(value)
                if isinstance(refined, ArithmeticMixin):
                    refinement1 = deepcopy(refined).mult(evaluation[expr.right])
                else:
                    refinement1 = deepcopy(refined).top()
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
                if isinstance(refined, ArithmeticMixin):
                    refinement2 = deepcopy(evaluation[expr.left]).div(refined)
                else:
                    refinement2 = deepcopy(refined).top()
                updated2 = self.visit(expr.right, evaluation, refinement2, updated1)
                return updated2
            raise ValueError(f"Binary arithmetic operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
        def visit_BinarySequenceOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).top()
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(refined).top()
                updated2 = self.visit(expr.right, evaluation, refinement2, updated1)
                return updated2
            raise ValueError(f"Binary arithmetic operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == BinaryBooleanOperation.Operator.And:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).top()
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(refined).top()
                updated2 = self.visit(expr.right, evaluation, refinement2, updated1)
                return updated2
            elif expr.operator == BinaryBooleanOperation.Operator.Or:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).top()
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(refined).top()
                updated2 = self.visit(expr.right, evaluation, refinement2, updated1)
                return updated2
            raise ValueError(f"Binary boolean operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

    _refinement = ExpressionRefinement()  # static class member shared between instances
