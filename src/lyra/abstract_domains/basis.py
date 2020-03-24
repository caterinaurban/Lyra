"""
Basis Abstract Domain
=====================

Interface of an abstract domain mapping variables to lattice elements.

:Author: Caterina Urban
"""
from abc import ABCMeta
from copy import deepcopy
from typing import Set, Dict, Type, Any

from lyra.abstract_domains.lattice import Lattice, ArithmeticMixin, BooleanMixin, SequenceMixin
from lyra.abstract_domains.state import State, StateWithSummarization
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, Slicing, \
    BinaryBooleanOperation, ExpressionVisitor, Literal, LengthIdentifier, ListDisplay, \
    AttributeReference, Input, Range, UnaryArithmeticOperation, BinaryArithmeticOperation, \
    UnaryBooleanOperation, TupleDisplay, SetDisplay, DictDisplay, BinarySequenceOperation, Keys, \
    Values, KeysIdentifier, ValuesIdentifier
from lyra.core.types import LyraType, BooleanLyraType, SequenceLyraType, DictLyraType
from lyra.core.utils import copy_docstring


class Basis(Store, State, metaclass=ABCMeta):
    """Analysis basis state. A mutable element of a basis abstract domain.
    (MRO: Basis, State, Store, EnvironmentMixin, Lattice)

    .. warning::
        Lattice operations and statements modify the current state.
    """

    def __init__(self, variables: Set[VariableIdentifier],
                 lattices: Dict[LyraType, Type[Lattice]],
                 arguments: Dict[LyraType, Dict[str, Any]] = None,
                 precursory: State = None):
        super().__init__(variables, lattices, arguments)
        State.__init__(self, precursory)

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'Basis':
        evaluation = self._evaluation.visit(right, self, dict())
        self.store[left] = evaluation[right]
        if isinstance(left.typ, DictLyraType):
            if isinstance(right.typ, DictLyraType):
                self.store[KeysIdentifier(left)] = evaluation[KeysIdentifier(right)]
                self.store[ValuesIdentifier(left)] = evaluation[ValuesIdentifier(right)]
            else:
                self.store[KeysIdentifier(left)] = deepcopy(evaluation[right])
                self.store[ValuesIdentifier(left)] = deepcopy(evaluation[right])
        return self

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

    @copy_docstring(State.forget_variable)
    def forget_variable(self, variable: VariableIdentifier) -> 'Basis':
        self.store[variable].top()
        if isinstance(variable.typ, DictLyraType):
            self.store[KeysIdentifier(variable)].top()
            self.store[ValuesIdentifier(variable)].top()
        return self

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'Basis':
        return self  # nothing to be done

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'State':
        # record the current value of the substituted variable
        value = deepcopy(self.store[left])
        # forget the current value of the substituted variable
        self.store[left].top()
        if isinstance(left.typ, DictLyraType):
            self.store[KeysIdentifier(left)].top()
            self.store[ValuesIdentifier(left)].top()
        # evaluate the right-hand side proceeding bottom-up using the updated store
        evaluation = self._evaluation.visit(right, self, dict())
        # check for errors turning the state into bottom
        feasible = evaluation[right].meet(value)
        if feasible.is_bottom():
            return self.bottom()
        # refine the updated store proceeding top-down on the right-hand side
        self._refinement.visit(right, evaluation, value, self)
        return self

    # expression evaluation

    class ExpressionEvaluation(ExpressionVisitor, metaclass=ABCMeta):
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

        def visit_KeysIdentifier(self, expr: KeysIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        def visit_ValuesIdentifier(self, expr: ValuesIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
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

        @copy_docstring(ExpressionVisitor.visit_Keys)
        def visit_Keys(self, expr: Keys, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            keys = KeysIdentifier(expr.target_dict)
            _evaluated = self.visit(keys, state, evaluation)
            evaluated = self.visit(expr.target_dict, state, evaluation)
            evaluation[expr] = _evaluated.get(keys, evaluated[expr.target_dict])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Values)
        def visit_Values(self, expr: Values, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            values = ValuesIdentifier(expr.target_dict)
            evaluated = self.visit(expr.target_dict, state, evaluation)
            evaluated_ = self.visit(values, state, evaluation)
            evaluation[expr] = evaluated_.get(values, evaluated[expr.target_dict])
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
            elif expr.operator == BinaryArithmeticOperation.Operator.Mod:
                if isinstance(value1, ArithmeticMixin):
                    evaluated2[expr] = deepcopy(value1).mod(value2)
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

    _evaluation: ExpressionEvaluation

    # expression refinement

    class ExpressionRefinement(ExpressionVisitor, metaclass=ABCMeta):
        """Visitor that:

        (1) refines the value of an evaluated expression based on a given lattice element; and
        (2) modifies the current state based on the refined value of the expression.
        """

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, evaluation=None, value=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, evaluation=None, value=None, state=None):
            if isinstance(expr.typ, DictLyraType):
                _refined = evaluation[KeysIdentifier(expr)].meet(value)
                state.store[KeysIdentifier(expr)] = _refined
            refined = evaluation[expr].meet(value)
            state.store[expr] = refined
            if isinstance(expr.typ, DictLyraType):
                refined_ = evaluation[ValuesIdentifier(expr)].meet(value)
                state.store[ValuesIdentifier(expr)] = refined_
            return state

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            state.store[expr] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Keys)
        def visit_Keys(self, expr: Keys, evaluation=None, value=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Values)
        def visit_Values(self, expr: Values, evaluation=None, value=None, state=None):
            return state  # nothing to be done

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
            elif expr.operator == BinaryArithmeticOperation.Operator.Mod:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).top()
                updated1 = self.visit(expr.left, evaluation, refinement1, state)
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

    _refinement: ExpressionRefinement


class BasisWithSummarization(StateWithSummarization, Basis, metaclass=ABCMeta):
    """Analysis basis state. A mutable element of a basis abstract domain.
    (MRO: BasisWithSummarization, StateWithSummarization, Store, EnvironmentMixin, State, Lattice)

    .. warning::
        Lattice operations and statements modify the current state.
    """

    @copy_docstring(StateWithSummarization._assign_dictionary_subscription)
    def _assign_dictionary_subscription(self, left: Subscription, right: Expression) -> 'StateWithSummarization':
        # copy the current state
        current: BasisWithSummarization = deepcopy(self)
        # perform the assignment on the copy of the current state
        target = left
        key = None
        while isinstance(target, Subscription):  # recurse to VariableIdentifier target
            key = target.key
            target = target.target
        # do self._assign_variable(target, right)
        _evaluation = self._evaluation.visit(key, self, dict())
        evaluation = self._evaluation.visit(right, self, dict())
        self.store[target] = deepcopy(evaluation[right]).join(deepcopy(_evaluation[key]))
        self.store[KeysIdentifier(target)] = _evaluation[key]
        self.store[ValuesIdentifier(target)] = evaluation[right]
        # perform a weak update on the current state
        return self.join(current)

    @copy_docstring(StateWithSummarization._weak_update)
    def _weak_update(self, variables: Set[VariableIdentifier], previous: 'BasisWithSummarization'):
        for var in variables:
            self.store[var].join(previous.store[var])
        return self

    # expression evaluation

    class ExpressionEvaluation(Basis.ExpressionEvaluation):

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
            _value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            value_ = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for key in expr.keys:
                evaluated = self.visit(key, state, evaluated)
                value = value.join(evaluated[key])
                _value = _value.join(evaluated[key])
            for val in expr.values:
                evaluated = self.visit(val, state, evaluated)
                value = value.join(evaluated[val])
                value_ = value_.join(evaluated[val])
            evaluation[KeysIdentifier(expr)] = _value
            evaluation[expr] = value
            evaluation[ValuesIdentifier(expr)] = value_
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            target = expr
            while isinstance(target, (Subscription, Slicing)):
                target = target.target
            evaluated = self.visit(target, state, evaluation)
            if isinstance(target.typ, DictLyraType):
                evaluated_ = self.visit(ValuesIdentifier(target), state, evaluation)
                evaluation[expr] = evaluated_.get(ValuesIdentifier(target), evaluated[target])
            else:
                evaluation[expr] = evaluated[target]
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            target = expr
            while isinstance(target, (Subscription, Slicing)):
                target = target.target
            evaluated = self.visit(target, state, evaluation)
            evaluation[expr] = evaluated[target]
            return evaluation

    _evaluation = ExpressionEvaluation()

    # expression refinement

    class ExpressionRefinement(Basis.ExpressionRefinement):

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

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, evaluation=None, value=None, state=None):
            refined = evaluation[expr]      # weak update
            target = expr
            while isinstance(target, (Subscription, Slicing)):
                target = target.target
            state.store[target] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, evaluation=None, value=None, state=None):
            refined = evaluation[expr]      # weak update
            target = expr
            while isinstance(target, (Subscription, Slicing)):
                target = target.target
            state.store[target] = refined
            return state

    _refinement = ExpressionRefinement()
