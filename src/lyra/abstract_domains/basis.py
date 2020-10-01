"""
Basis Abstract Domain
=====================

Interface of an abstract domain mapping variables to lattice elements.

:Author: Caterina Urban
"""
from abc import ABCMeta
from ast import literal_eval
from copy import deepcopy
from typing import Set, Dict, Type, Any, Union, List

from lyra.abstract_domains.container.indexed_lattice import IndexedLattice
from lyra.abstract_domains.lattice import Lattice, ArithmeticMixin, BooleanMixin, SequenceMixin
from lyra.abstract_domains.numerical.interval_lattice import IntervalLattice
from lyra.abstract_domains.state import State, StateWithSummarization
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, Slicing, \
    BinaryBooleanOperation, ExpressionVisitor, Literal, LengthIdentifier, ListDisplay, \
    AttributeReference, Input, Range, UnaryArithmeticOperation, BinaryArithmeticOperation, \
    UnaryBooleanOperation, TupleDisplay, SetDisplay, DictDisplay, BinarySequenceOperation, Keys, \
    Values, KeysIdentifier, ValuesIdentifier, CastOperation, BinaryComparisonOperation
from lyra.core.types import LyraType, BooleanLyraType, SequenceLyraType, DictLyraType, \
    ContainerLyraType, IntegerLyraType, FloatLyraType, StringLyraType, ListLyraType, SetLyraType, \
    TupleLyraType
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
        if self.is_bottom():
            return self
        self.store[left] = evaluation[right]
        if left.has_length:
            self.lengths[left.length] = evaluation[LengthIdentifier(right)]
            if left.is_dictionary:
                if isinstance(right.typ, DictLyraType):
                    self.keys[left.keys] = evaluation[KeysIdentifier(right)]
                    self.values[left.values] = evaluation[ValuesIdentifier(right)]
                else:
                    self.keys[left.keys] = deepcopy(evaluation[right])
                    self.values[left.values] = deepcopy(evaluation[right])
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
        if variable.has_length:
            self.lengths[variable.length] = IntervalLattice(lower=0)
            if variable.is_dictionary:
                self.keys[variable.keys].top()
                self.values[variable.values].top()
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
        if left.has_length:
            self.lengths[left.length] = IntervalLattice(lower=0)
            if left.is_dictionary:
                self.keys[left.keys].top()
                self.values[left.values].top()
        # evaluate the right-hand side proceeding bottom-up using the updated store
        evaluation = self._evaluation.visit(right, self, dict())
        if self.is_bottom():
            return self
        # check for errors turning the state into bottom
        if not evaluation[right].is_bottom():
            feasible = deepcopy(evaluation[right]).meet(value)
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
            if isinstance(expr.typ, StringLyraType):
                evaluation[LengthIdentifier(expr)] = IntervalLattice(len(expr.val), len(expr.val))
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.store[expr])
            if expr.has_length:
                evaluation[expr.length] = deepcopy(state.lengths[expr.length])
                if expr.is_dictionary:
                    evaluation[expr.keys] = deepcopy(state.keys[expr.keys])
                    evaluation[expr.values] = deepcopy(state.values[expr.values])
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr: LengthIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            evaluated[expr] = evaluated[LengthIdentifier(expr.expression)]
            return evaluated

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
                if isinstance(expr.typ, (SequenceLyraType, DictLyraType)):
                    evaluation[LengthIdentifier(expr)] = IntervalLattice(lower=0)
                    if isinstance(expr.typ, DictLyraType):
                        k = state.lattices[expr.typ.key_typ](**state.arguments[expr.typ.key_typ])
                        evaluation[KeysIdentifier(expr)] = k.top()
                        v = state.lattices[expr.typ.key_typ](**state.arguments[expr.typ.key_typ])
                        evaluation[ValuesIdentifier(expr)] = v.top()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
            evaluation[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if state.is_bottom():
                return evaluation
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
            if state.is_bottom():
                return evaluation
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
            if state.is_bottom():
                return evaluation
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if state.is_bottom():
                return evaluation
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

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            if state.is_bottom():
                return evaluation
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if state.is_bottom():
                return evaluation
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

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            state.lengths[expr] = refined
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

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression):
        """The subscription assignment is of the form target[key] = value. There are various cases:

        * target is a variable (i.e., simple subscription); in this case we should
            (1) (list) join value to the summary corresponding to target
                (dictionary) join key and value to the summary corresponding to target
            (2) (list) check that key is in length bounds of target
                (list/dictionary) update length of target
            (3) (dictionary) join key to the summary of the keys of target
            (4) (dictionary) join value fo the summary of the values of target
        * target is a subscription or a slicing (i.e., nested subscription);
            (1) recursively find the target of the target, i.e., x
                (if at any point a slicing is encountered, the assignment has *no effect* on x)
            (2) (list) join value to the summary corresponding to x, and
                if x is a dictionary, join value to the summary of the values of x
                note that i, j, ... must already be in the summary of the keys of x
                (dictionary) join key and value to the summary corresponding to x, and
                if x is a dictionary, join key and value to the summary of the values of x
                note that i, j, ... must already be in the summary of the keys of x
        """
        evaluation = self._evaluation.visit(left.key, self, dict())     # evaluate key
        if self.is_bottom():
            return self
        key = evaluation[left.key]
        evaluation = self._evaluation.visit(right, self, dict())        # evaluate value
        if self.is_bottom():
            return self
        value = evaluation[right]
        # perform a weak update on the current state
        target = left.target
        if isinstance(target, VariableIdentifier):      # simple subscription: x[key] = value
            if isinstance(target.typ, ListLyraType):            # l[key] = value
                self.store[target] = self.store[target].join(deepcopy(value))
                if isinstance(key, IntervalLattice):
                    length: IntervalLattice = self.lengths[target.length]
                    if 0 <= key.lower:  # key is positive
                        if length.upper <= key.lower:       # key is definitely larger than length
                            return self.bottom()
                        lower = IntervalLattice(lower=key.lower + 1)
                        self.lengths[target.length] = length.meet(lower)
                    elif key.upper < 0:  # key is negative
                        if length.upper + key.upper < 0:    # key is definitely smaller than length
                            return self.bottom()
                        upper = IntervalLattice(lower=-key.upper)
                        self.lengths[target.length] = length.meet(upper)
            else:
                assert isinstance(target.typ, DictLyraType)     # d[key] = value
                self.store[target] = self.store[target].join(deepcopy(key)).join(deepcopy(value))
                length: IntervalLattice = self.lengths[target.length]
                one = IntervalLattice(lower=1, upper=1)
                intersection = deepcopy(key).meet(deepcopy(self.keys[target.keys]))
                if intersection.is_bottom():  # key does not belong to target keys
                    self.lengths[target.length] = length.add(one)
                else:
                    self.lengths[target.length] = deepcopy(length).join(length.add(one))
                # in any case the dictionary contains at least one key now
                one_ = IntervalLattice(lower=1)
                self.lengths[target.length] = self.lengths[target.length].meet(one_)
                self.keys[target.keys] = self.keys[target.keys].join(key)
                self.values[target.values] = self.values[target.values].join(value)
        else:   # nested subscription: X[key] = value
            assert isinstance(target, (Subscription, Slicing))
            if isinstance(target.typ, ListLyraType):            # L[key] = value
                while isinstance(target, Subscription):
                    target = target.target
                if isinstance(target, Slicing):
                    return self
                assert isinstance(target, VariableIdentifier)
                self.store[target] = self.store[target].join(deepcopy(value))
                if isinstance(target.typ, DictLyraType):    # d[...][key] = value
                    self.values[target.values] = self.values[target.values].join(deepcopy(value))
            else:
                assert isinstance(target.typ, DictLyraType)     # D[key] = value
                while isinstance(target, Subscription):
                    target = target.target
                assert isinstance(target, VariableIdentifier)
                joined = deepcopy(key).join(deepcopy(value))
                self.store[target] = self.store[target].join(deepcopy(joined))
                if isinstance(target.typ, DictLyraType):    # d[...][key] = value
                    self.values[target.values] = self.values[target.values].join(deepcopy(joined))
        return self

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'StateWithSummarization':
        """The slicing assignment is of the form target[...] = value.
        This corresponds to the default case for a subscription (see above),
        with the exception of an assignment of the form x[i:j]...[k:l]
        which again has *no effect* on x."""
        evaluation = self._evaluation.visit(right, self, dict())      # evaluate value
        if self.is_bottom():
            return self
        value = evaluation[right]
        # perform a weak update on the current state
        target = left.target
        if isinstance(target, VariableIdentifier):      # simple slicing: x[i:j] = value
            if isinstance(target.typ, ListLyraType):    # l[i:j] = value
                self.store[target] = self.store[target].join(deepcopy(value))
                length: IntervalLattice = self.lengths[target.length]
                slicing = IntervalLattice(lower=1, upper=1) # default under-approximation
                extra = self._length.visit(right, self)     # over-approximate length of right
                # len(x) = len(x) - len(x[j:i]) + len(e)
                self.lengths[target.length] = length.sub(slicing).add(extra)
        else:   # nested slicing: X[i:j] = value
            assert isinstance(target, (Subscription, Slicing))
            while isinstance(target, Subscription):
                target = target.target
            if isinstance(target, Slicing):
                return self
            assert isinstance(target, VariableIdentifier)
            self.store[target] = self.store[target].join(deepcopy(value))
            if target.is_dictionary:
                self.values[target.values] = self.values[target.values].join(deepcopy(value))
        return self

    @copy_docstring(StateWithSummarization._weak_update)
    def _weak_update(self, variables: Set[VariableIdentifier], previous: 'BasisWithSummarization'):
        for var in variables:
            self.store[var].join(previous.store[var])
            if var.is_dictionary:
                self.keys[var.keys].join(previous.keys[var.keys])
                self.values[var.values].join(previous.values[var.values])
        return self

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression):
        # copy the current state
        current: BasisWithSummarization = deepcopy(self)
        # perform the substitution on the copy of the current state
        target = left
        while isinstance(target, (Subscription, Slicing)):  # recurse to VariableIdentifier target
            target = target.target
        if isinstance(left.target, VariableIdentifier) and left.target.is_dictionary:
            # update length
            length = self.lengths[left.target.length]
            one = IntervalLattice(lower=1, upper=1)
            updated = IntervalLattice(lower=0).meet(deepcopy(length).join(length.sub(one)))
            self.lengths[left.target.length] = updated

        # record the current value of the substituted variable
        value = deepcopy(self.store[target])
        # forget the current value of the substituted variable
        self.store[target].top()
        if target.is_dictionary:
            self.keys[target.keys].top()
            self.values[target.values].top()
        # evaluate the right-hand side proceeding bottom-up using the updated store
        evaluation = self._evaluation.visit(right, self, dict())
        if self.is_bottom():
            return self
        # check for errors turning the state into bottom
        if not evaluation[right].is_bottom():
            feasible = deepcopy(evaluation[right]).meet(value)
            if feasible.is_bottom():
                return self.bottom()
        # refine the updated store proceeding top-down on the right-hand side
        self._refinement.visit(right, evaluation, value, self)

        # check for errors turning the state into bottom
        if self.is_bottom():
            return self
        # if there are not errors, perform a weak update on the current state
        return self.join(current)

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'BasisWithSummarization':
        # copy the current state
        current: BasisWithSummarization = deepcopy(self)
        # perform the substitution on the copy of the current state
        target = left
        while isinstance(target, (Subscription, Slicing)):  # recurse to VariableIdentifier target
            target = target.target

        # record the current value of the substituted variable
        value = deepcopy(self.store[target])
        # forget the current value of the substituted variable
        self.store[target].top()
        if target.is_dictionary:
            self.keys[target.keys].top()
            self.values[target.values].top()
        # evaluate the right-hand side proceeding bottom-up using the updated store
        evaluation = self._evaluation.visit(right, self, dict())
        if self.is_bottom():
            return self
        # check for errors turning the state into bottom
        if not evaluation[right].is_bottom():
            feasible = deepcopy(evaluation[right]).meet(value)
            if feasible.is_bottom():
                return self.bottom()
        # refine the updated store proceeding top-down on the right-hand side
        self._refinement.visit(right, evaluation, value, self)

        # check for errors turning the state into bottom
        if self.is_bottom():
            return self
        # if there are not errors, perform a weak update on the current state
        return self.join(current)

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
                if state.is_bottom():
                    return evaluation
                value = value.join(evaluated[item])
            evaluated[expr] = value
            evaluated[LengthIdentifier(expr)] = IntervalLattice(len(expr.items), len(expr.items))
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                if state.is_bottom():
                    return evaluation
                value = value.join(evaluated[item])
            evaluated[expr] = value
            evaluated[LengthIdentifier(expr)] = IntervalLattice(len(expr.items), len(expr.items))
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                if state.is_bottom():
                    return evaluation
                value = value.join(evaluated[item])
            evaluated[expr] = value
            evaluated[LengthIdentifier(expr)] = IntervalLattice(len(expr.items), len(expr.items))
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            _value = state.lattices[expr.typ.key_typ](**state.arguments[expr.typ.key_typ]).bottom()
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            value_ = state.lattices[expr.typ.val_typ](**state.arguments[expr.typ.val_typ]).bottom()
            for key, val in zip(expr.keys, expr.values):
                evaluated = self.visit(key, state, evaluated)
                if state.is_bottom():
                    return evaluation
                value = value.join(evaluated[key])
                _value = _value.join(evaluated[key])
                #
                evaluated = self.visit(val, state, evaluated)
                if state.is_bottom():
                    return evaluation
                value = value.join(evaluated[val])
                value_ = value_.join(evaluated[val])
            evaluated[expr] = value
            evaluated[LengthIdentifier(expr)] = IntervalLattice(len(expr.keys), len(expr.keys))
            evaluated[KeysIdentifier(expr)] = _value
            evaluated[ValuesIdentifier(expr)] = value_
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target, state, evaluation)  # evaluate target
            if state.is_bottom():
                return evaluation
            target = evaluated[expr.target]
            evaluated = self.visit(expr.key, state, evaluated)      # evaluate key
            if state.is_bottom():
                return evaluation
            key = evaluated[expr.key]
            if isinstance(expr.target.typ, SequenceLyraType):
                # check (and modify) target length based on key
                if isinstance(key, IntervalLattice):
                    length: IntervalLattice = evaluated[LengthIdentifier(expr.target)]
                    if 0 <= key.lower:  # key is positive
                        if length.upper <= key.lower:  # key is larger than length
                            state.bottom()
                            return evaluation
                        lower = IntervalLattice(lower=key.lower + 1)
                        if isinstance(expr.target, VariableIdentifier):
                            state.lengths[expr.target.length] = length.meet(lower)
                    elif key.upper < 0:  # key is negative
                        if length.upper + key.upper < 0:  # key is smaller than length
                            state.bottom()
                            return evaluation
                        upper = IntervalLattice(lower=-key.upper)
                        if isinstance(expr.target, VariableIdentifier):
                            state.lengths[expr.target.length] = length.meet(upper)
                evaluated[expr] = deepcopy(target)  # return value of target
                if isinstance(expr.typ, (StringLyraType, ContainerLyraType)):
                    if isinstance(expr.target.typ, StringLyraType):
                        evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=1, upper=1)
                    else:
                        evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
                        if isinstance(expr.typ, DictLyraType):
                            evaluated[KeysIdentifier(expr)] = deepcopy(target)
                            evaluated[ValuesIdentifier(expr)] = deepcopy(target)
            else:
                assert isinstance(expr.target.typ, DictLyraType)
                keys = evaluated[KeysIdentifier(expr.target)]
                values = evaluated[ValuesIdentifier(expr.target)]
                # check (and modify) target length based on key
                intersection = deepcopy(key).meet(deepcopy(keys))
                if intersection.is_bottom():  # key does not belong to target keys
                    state.bottom()
                    return evaluation
                if isinstance(expr.target, VariableIdentifier):
                    length: IntervalLattice = state.lengths[expr.target.length]
                    state.lengths[expr.target.length] = length.meet(IntervalLattice(lower=1))
                # return value of target values
                evaluated[expr] = deepcopy(values)
                if isinstance(expr.typ, (StringLyraType, ContainerLyraType)):
                    evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
                    if isinstance(expr.typ, DictLyraType):
                        evaluated[KeysIdentifier(expr)] = deepcopy(values)
                        evaluated[ValuesIdentifier(expr)] = deepcopy(values)
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            target = expr
            while isinstance(target, (Subscription, Slicing)):
                target = target.target
            evaluated = self.visit(target, state, evaluation)
            if state.is_bottom():
                return evaluation
            evaluated[expr] = deepcopy(evaluated[target])
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_Keys)
        def visit_Keys(self, expr: Keys, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target_dict, state, evaluation)
            if state.is_bottom():
                return evaluation
            assert isinstance(expr.typ, SetLyraType)
            keys = evaluated[KeysIdentifier(expr.target_dict)]
            evaluated[expr] = deepcopy(keys)
            evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_Values)
        def visit_Values(self, expr: Values, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target_dict, state, evaluation)
            if state.is_bottom():
                return evaluation
            values = evaluated[ValuesIdentifier(expr.target_dict)]
            assert isinstance(expr.typ, SetLyraType)
            evaluated[expr] = deepcopy(values)
            evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_CastOperation)
        def visit_CastOperation(self, expr: CastOperation, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if state.is_bottom():
                return evaluation
            iscontainer = isinstance(expr.expression.typ, (SequenceLyraType, ContainerLyraType))
            if isinstance(expr.typ, BooleanLyraType) and iscontainer:
                if evaluated[expr.expression].is_bottom():
                    value = state.lattices[expr.typ](**state.arguments[expr.typ]).false()
                else:
                    value = state.lattices[expr.typ](**state.arguments[expr.typ]).true()
                evaluated[expr] = value
            elif isinstance(expr.typ, StringLyraType):
                value = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                evaluation[expr] = value
                evaluation[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            else:
                evaluated[expr] = deepcopy(evaluated[expr.expression])
                if isinstance(expr.typ, (SequenceLyraType, ContainerLyraType)):
                    default: IntervalLattice = IntervalLattice(lower=0)
                    length = evaluation.get(LengthIdentifier(expr.expression), default)
                    evaluation[LengthIdentifier(expr)] = length
                    if isinstance(expr.typ, DictLyraType):
                        evaluation[KeysIdentifier(expr)] = deepcopy(evaluated[expr.expression])
                        evaluation[ValuesIdentifier(expr)] = deepcopy(evaluated[expr.expression])
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
        def visit_BinarySequenceOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            if state.is_bottom():
                return evaluation
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if state.is_bottom():
                return evaluation
            value1 = evaluated2[expr.left]
            len1 = evaluated2[LengthIdentifier(expr.left)]
            value2 = evaluated2[expr.right]
            len2 = evaluated2[LengthIdentifier(expr.right)]
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                if isinstance(value1, SequenceMixin):
                    if isinstance(expr.typ, ContainerLyraType):     # summarization
                        evaluated2[expr] = deepcopy(value1).join(value2)
                    else:
                        evaluated2[expr] = deepcopy(value1).concat(value2)
                    evaluated2[LengthIdentifier(expr)] = deepcopy(len1).add(deepcopy(len2))
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                    evaluated2[LengthIdentifier(expr)] = IntervalLattice(lower=0)
                return evaluated2
            raise ValueError(f"Binary sequence operator '{str(expr.operator)}' is unsupported!")

    _evaluation = ExpressionEvaluation()

    # expression refinement

    class ExpressionRefinement(Basis.ExpressionRefinement):

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            state.store[expr] = refined
            if expr.is_dictionary:
                _refined = evaluation[expr.keys].meet(value)
                state.keys[expr.keys] = _refined
                refined_ = evaluation[expr.values].meet(value)
                state.values[expr.values] = refined_
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

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, evaluation=None, value=None, state=None):
            refined = evaluation[expr]      # weak update
            updated = self.visit(expr.target, evaluation, refined, state)
            key = evaluation[expr.key]
            if isinstance(expr.target.typ, SequenceLyraType):
                if isinstance(key, IntervalLattice):
                    length: IntervalLattice = evaluation[LengthIdentifier(expr.target)]
                    if 0 <= key.lower:  # key is positive
                        lower = IntervalLattice(lower=key.lower + 1)
                        if isinstance(expr.target, VariableIdentifier):
                            updated.lengths[expr.target.length] = length.meet(lower)
                    elif key.upper < 0:  # key is negative
                        upper = IntervalLattice(lower=-key.upper)
                        if isinstance(expr.target, VariableIdentifier):
                            updated.lengths[expr.target.length] = length.meet(upper)
            else:
                assert isinstance(expr.target.typ, DictLyraType)
                if isinstance(expr.target, VariableIdentifier):
                    length: IntervalLattice = state.lengths[expr.target.length]
                    state.lengths[expr.target.length] = length.meet(IntervalLattice(lower=1))
            return updated

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, evaluation=None, value=None, state=None):
            refined = evaluation[expr]      # weak update
            target = expr
            while isinstance(target, (Subscription, Slicing)):
                target = target.target
            state.store[target] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_CastOperation)
        def visit_CastOperation(self, expr, evaluation=None, value=None, state=None):
            assert not isinstance(expr.expression.typ, type(expr.typ))  # there is actually a cast
            if isinstance(expr.typ, BooleanLyraType):   # y = cast(x)
                if isinstance(expr.expression.typ, (IntegerLyraType, FloatLyraType)):
                    refined = evaluation[expr].meet(value)
                    return self.visit(expr.expression, evaluation, refined, state)
                assert isinstance(expr.expression, (SequenceLyraType, ContainerLyraType))
                refined = evaluation[expr].meet(value)
                assert isinstance(refined, BooleanMixin)
                if refined.is_false():      # x is empty
                    typ = expr.expression.typ
                    _refined = state.lattices[typ](**state.arguments[typ]).bottom()
                    return self.visit(expr.expression, evaluation, _refined, state)
                else:                       # x could be empty or non-empty
                    return state    # over-approximation
            elif isinstance(expr.typ, (IntegerLyraType, FloatLyraType)):
                typ = expr.expression.typ
                simple = (BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType)
                assert isinstance(typ, simple)
                refined = evaluation[expr].meet(value)
                return self.visit(expr.expression, evaluation, refined, state)
            elif isinstance(expr.typ, StringLyraType):
                return state    # over-approximation
            elif isinstance(expr.typ, (ListLyraType, SetLyraType, TupleLyraType)):
                if isinstance(expr.expression.typ, DictLyraType):
                    return state    # over-approximation
                refined = evaluation[expr].meet(value)
                return self.visit(expr.expression, evaluation, refined, state)
            else:
                error = f"Cast to {expr.typ} of expression {expr.expression} is unexpected!"
                raise ValueError(error)

    _refinement = ExpressionRefinement()


class BasisWithIndexing(Basis, metaclass=ABCMeta):
    """Basis abstract domain with indexing (and summarization for sets).

    .. warning::
        Lattice operations and statements modify the current state.
    """

    @copy_docstring(Basis._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression):
        """The subscription assignment is of the form target[key] = value. There are various cases:

        * target is a variable (i.e., simple subscription); in this case we should
            (1) update the indexed value corresponding to target
            (2) (list) check that key is in length bounds of target
                (list/dictionary) update length of target
            (3) (dictionary) update keys of target
            (4) (dictionary) update values of target
        * target is a subscription or a slicing (i.e., nested subscription);
            (1) recursively find the target of the target, i.e., x
                (if at any point a slicing is encountered, the assignment has *no effect* on x)
            (2) (list) update the value corresponding to x with value, and
                if x is a dictionary, update values of x with value
                note that i, j, ... must already be in the summary of the keys of x
                (dictionary) update the value corresponding to x with key and value, and
                if x is a dictionary, update values of x with key and value
                note that i, j, ... must already be in the summary of the keys of x
        """
        evaluation = self._evaluation.visit(left.key, self, dict())             # evaluate key
        if self.is_bottom():
            return self
        key = evaluation[left.key]
        evaluation = self._evaluation.visit(right, self, dict())                # evaluate value
        if self.is_bottom():
            return self
        value = evaluation[right]
        if isinstance(value, IndexedLattice):                                   # summarize value
            if isinstance(left.target.typ.val_typ, DictLyraType):
                itv = value.summarize(keys=left.target.typ.val_typ.key_typ)
            else:
                itv = value.summarize()
        else:
            itv = deepcopy(value)
        # perform a strong update on the current state
        if isinstance(left.target, VariableIdentifier):      # simple subscription: x[key] = value
            evaluation = self._evaluation.visit(left.target, self, dict())      # evaluate target
            if self.is_bottom():
                return self
            target: IndexedLattice = evaluation[left.target]
            _key: List[str] = self._key.visit(left.key, target.bound, self)
            precise = len(_key) == 1 and _key[0] != target.default
            added, replaced = False, False
            if precise:
                added = _key[0] not in target.used and target.default not in target.used
                replaced = _key[0] in target.used
                self.store[left.target][_key[0]] = itv
            else:
                self.store[left.target].weak_set(_key, itv)
            if isinstance(left.target.typ, ListLyraType):               # l[key] = value
                if isinstance(key, IntervalLattice):
                    length: IntervalLattice = self.lengths[left.target.length]
                    if 0 <= key.lower:  # key is positive
                        if length.upper <= key.lower:       # key is definitely larger than length
                            return self.bottom()
                        lower = IntervalLattice(lower=key.lower + 1)
                        self.lengths[left.target.length] = length.meet(lower)
                    elif key.upper < 0:  # key is negative
                        if length.upper + key.upper < 0:    # key is definitely smaller than length
                            return self.bottom()
                        upper = IntervalLattice(lower=-key.upper)
                        self.lengths[left.target.length] = length.meet(upper)
            else:
                assert isinstance(left.target.typ, DictLyraType)        # d[key] = value
                # update length
                length: IntervalLattice = self.lengths[left.target.length]  # current length
                one = IntervalLattice(lower=1, upper=1)
                if precise:
                    if added:
                        self.lengths[left.target.length] = length.add(one)
                    elif not replaced:
                        self.lengths[left.target.length] = deepcopy(length).join(length.add(one))
                else:
                    self.lengths[left.target.length] = deepcopy(length).join(length.add(one))
                # in any case the dictionary contains at least one key now
                one_ = IntervalLattice(lower=1)
                self.lengths[left.target.length] = self.lengths[left.target.length].meet(one_)
                # update keys
                self.keys[left.target.keys] = self.keys[left.target.keys].join(deepcopy(key))
                # update values
                summary = self.store[left.target].summarize()
                values = left.target.values
                if isinstance(self.values[values], IndexedLattice):
                    assert isinstance(value, IndexedLattice)
                    updated = self.values[values].join(deepcopy(value)).refine(summary)
                    self.values[values] = updated
                else:
                    self.values[values] = self.values[values].join(deepcopy(itv)).meet(summary)
        else:   # nested subscription: X[key] = value
            assert isinstance(left.target, (Subscription, Slicing))
            if isinstance(left.target.typ, ListLyraType):           # L[key] = value
                _target = left.target.target
                _key = left.target.key
                __key = left.key
                while isinstance(_target, Subscription):
                    __key = _key
                    _key = _target.key
                    _target = _target.target
                if isinstance(_target, Slicing):
                    return self
                assert isinstance(_target, VariableIdentifier)
                evaluation = self._evaluation.visit(_target, self, dict())
                if self.is_bottom():
                    return self
                target = evaluation[_target]
                _key: List[str] = self._key.visit(_key, target.bound, self)
                self.store[_target].weak_set(_key, itv)
                if isinstance(_target.typ, DictLyraType):    # d[...][key] = value
                    summary = self.store[_target].summarize()
                    values = _target.values
                    if isinstance(self.values[values], IndexedLattice):
                        __key: List[str] = self._key.visit(__key, target.bound, self)
                        self.values[values].weak_set(__key, itv)
                        self.values[values] = self.values[values].refine(summary)
                    else:
                        self.values[values] = self.values[values].join(deepcopy(itv)).meet(summary)
            else:
                assert isinstance(left.target.typ, DictLyraType)    # D[key] = value
                _target = left.target.target
                _key = left.target.key
                __key = left.key
                while isinstance(_target, Subscription):
                    __key = _key
                    _key = _target.key
                    _target = _target.target
                assert isinstance(_target, VariableIdentifier)
                evaluation = self._evaluation.visit(_target, self, dict())
                if self.is_bottom():
                    return self
                target = evaluation[_target]
                _key: List[str] = self._key.visit(_key, target.bound, self)
                _itv = key.summarize() if isinstance(key, IndexedLattice) else deepcopy(key)
                joined = deepcopy(itv).join(deepcopy(_itv))
                self.store[_target].weak_set(_key, joined)
                if isinstance(_target.typ, DictLyraType):    # d[...][key] = value
                    summary = self.store[_target].summarize()
                    values = _target.values
                    if isinstance(self.values[values], IndexedLattice):
                        __key: List[str] = self._key.visit(__key, target.bound, self)
                        self.values[values].weak_set(__key, itv)
                        self.values[values] = self.values[values].refine(summary)
                    else:
                        self.values[values] = self.values[values].join(deepcopy(itv)).meet(summary)
        return self

    @copy_docstring(Basis._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression):
        raise NotImplementedError  # TODO

    @copy_docstring(Basis._assume_binary_comparison)
    def _assume_binary_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # identify involved set identifiers
        containers = {var for var in condition.ids() if isinstance(var.typ, SetLyraType)}
        # expand, i.e., copy the current state, if needed
        current = deepcopy(self) if containers else None
        # perform the assumption on the current state
        if condition.operator == BinaryComparisonOperation.Operator.Eq:
            self._assume_eq_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.NotEq:
            self._assume_noteq_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.Lt:
            self._assume_lt_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.LtE:
            self._assume_lte_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.Gt:
            self._assume_gt_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.GtE:
            self._assume_gte_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.Is:
            self._assume_is_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.IsNot:
            self._assume_isnot_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.In:
            self._assume_in_comparison(condition, bwd=bwd)
        else:
            assert condition.operator == BinaryComparisonOperation.Operator.NotIn
            self._assume_notin_comparison(condition, bwd=bwd)
        # fold, i.e., perform a weak update on the current state, if needed
        for container in containers:
            assert isinstance(container.typ, SetLyraType)
            self.store[container].join(current.store[container])
        return self

    @copy_docstring(Basis._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression):
        if isinstance(left.target, VariableIdentifier):
            evaluation = self._evaluation.visit(left.target, self, dict())
            if self.is_bottom():
                return self
            target: IndexedLattice = evaluation[left.target]
            _key: List[str] = self._key.visit(left.key, target.bound, self)
            # record the current value of the subscription
            evaluation = self._evaluation.visit(left, self, dict())
            if self.is_bottom():
                return self
            current = evaluation[left]
            # forget the current value of the subscription
            self.store[left.target].forget(_key)
            if left.target.is_dictionary:
                # update length
                length = self.lengths[left.target.length]
                default = IntervalLattice(lower=0)
                one = IntervalLattice(lower=1, upper=1)
                updated = default.meet(deepcopy(length).join(length.sub(one)))
                self.lengths[left.target.length] = updated
                # forget keys and values
                self.keys[left.target.keys] = self.keys[left.target.keys].top()
                self.values[left.target.values] = self.values[left.target.values].top()
            # evaluate the right-hand side proceeding bottom-up using the updated store
            evaluation = self._evaluation.visit(right, self, dict())
            if self.is_bottom():
                return self
            # check for errors turning the state into bottom
            if not evaluation[right].is_bottom():
                feasible = deepcopy(evaluation[right]).meet(current)
                if feasible.is_bottom():
                    return self.bottom()
            # refine the updated store proceeding top-down on the right-hand side
            self._refinement.visit(right, evaluation, current, self)
        else:
            raise NotImplementedError  # TODO
        return self

    @copy_docstring(Basis._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression):
        raise NotImplementedError  # TODO

    # key evaluation

    class KeyEvaluation(ExpressionVisitor):

        def visit_Literal(self, expr: 'Literal', bound=None, state=None) -> List[str]:
            return [str(expr)]

        def default(self, expr, bound=None, state=None) -> List[str]:
            current = state._evaluation.visit(expr, state, dict())[expr]
            itv = current.summarize() if isinstance(current, IndexedLattice) else current
            return itv.gamma(bound)

        def visit_VariableIdentifier(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_LengthIdentifier(self, expr: 'LengthIdentifier', bound=None, state=None):
            return self.default(expr, bound, state)

        def visit_ListDisplay(self, expr: 'ListDisplay', bound=None, state=None):
            raise ValueError(f"Unexpected expression during key evaluation.")

        def visit_TupleDisplay(self, expr: 'TupleDisplay', bound=None, state=None) -> List[str]:
            items = list()
            for item in expr.items:
                value: List[str] = self.visit(item, bound, state)
                if len(value) == 1:
                    items.append(value[0])
                else:
                    return ['_']
            return ['({})'.format(', '.join(items))]

        def visit_SetDisplay(self, expr: 'SetDisplay', bound=None, state=None):
            raise ValueError(f"Unexpected expression during key evaluation.")

        def visit_DictDisplay(self, expr: 'DictDisplay', bound=None, state=None):
            raise ValueError(f"Unexpected expression during key evaluation.")

        def visit_AttributeReference(self, expr: 'AttributeReference', bound=None, state=None):
            raise NotImplementedError(f"Unsupported expression during key evaluation.")

        def visit_Subscription(self, expr: 'Subscription', bound=None, state=None) -> List[
            str]:
            return self.default(expr, bound, state)

        def visit_Slicing(self, expr: 'Slicing', bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_Input(self, expr: 'Input', bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_Range(self, expr: 'Range', bound=None, state=None):
            raise NotImplementedError(f"Unsupported expression during key evaluation.")

        def visit_Keys(self, expr: 'Keys', bound=None, state=None):
            raise NotImplementedError(f"Unsupported expression during key evaluation.")

        def visit_Values(self, expr: 'Values', bound=None, state=None):
            raise NotImplementedError(f"Unsupported expression during key evaluation.")

        def visit_CastOperation(self, expr: 'CastOperation', bound=None, state=None) -> List[
            str]:
            return self.default(expr, bound, state)

        def visit_UnaryArithmeticOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_UnaryBooleanOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_BinaryArithmeticOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_BinarySequenceOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_BinaryBooleanOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

        def visit_BinaryComparisonOperation(self, expr, bound=None, state=None) -> List[str]:
            return self.default(expr, bound, state)

    _key = KeyEvaluation()

    # expression evaluation

    class ExpressionEvaluation(Basis.ExpressionEvaluation):

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: 'ListDisplay', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ], index=dict())
            for idx, item in enumerate(expr.items):
                evaluated = self.visit(item, state, evaluated)
                if state.is_bottom():
                    return evaluation
                current = evaluated[item]
                if isinstance(current, IndexedLattice):
                    if isinstance(expr.typ.typ, DictLyraType):
                        itv = current.summarize(keys=expr.typ.typ.key_typ)
                    else:
                        itv = current.summarize()
                else:
                    itv = deepcopy(current)
                value[str(idx)] = itv
            evaluated[expr] = value
            evaluated[LengthIdentifier(expr)] = IntervalLattice(len(expr.items), len(expr.items))
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: 'TupleDisplay', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ], index=dict())
            for idx, item in enumerate(expr.items):
                evaluated = self.visit(item, state, evaluated)
                if state.is_bottom():
                    return evaluation
                current = evaluated[item]
                if isinstance(current, IndexedLattice):
                    if isinstance(expr.typ.typs[idx], DictLyraType):
                        itv = current.summarize(keys=expr.typ.typs[idx].key_typ)
                    else:
                        itv = current.summarize()
                else:
                    itv = deepcopy(current)
                value[str(idx)] = itv
            evaluated[expr] = value
            evaluated[LengthIdentifier(expr)] = IntervalLattice(len(expr.items), len(expr.items))
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: 'SetDisplay', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            value = state.lattices[expr.typ](**state.arguments[expr.typ]).bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                if state.is_bottom():
                    return evaluation
                current = evaluated[item]
                if isinstance(current, IndexedLattice):
                    if isinstance(expr.typ.typ, DictLyraType):
                        itv = current.summarize(keys=expr.typ.typ.key_typ)
                    else:
                        itv = current.summarize()
                else:
                    itv = deepcopy(current)
                value = value.join(itv)
            evaluated[expr] = value
            evaluated[LengthIdentifier(expr)] = IntervalLattice(len(expr.items), len(expr.items))
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: 'DictDisplay', state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            _value = state.lattices[expr.typ.key_typ](**state.arguments[expr.typ.key_typ]).bottom()
            value = state.lattices[expr.typ](**state.arguments[expr.typ], index=dict())
            value_ = state.lattices[expr.typ.val_typ](**state.arguments[expr.typ.val_typ]).bottom()
            for key, val in zip(expr.keys, expr.values):
                evaluated = self.visit(key, state, evaluated)  # recurse on key
                if state.is_bottom():
                    return evaluation
                _current: Lattice = evaluated[key]
                _value = _value.join(deepcopy(_current))
                #
                evaluated = self.visit(val, state, evaluated)  # recurse on val
                if state.is_bottom():
                    return evaluation
                current_: Lattice = evaluated[val]
                if isinstance(expr.typ.val_typ, DictLyraType):
                    value_ = value_.merge(deepcopy(current_), keys=expr.typ.val_typ.key_typ)
                else:
                    value_ = value_.join(deepcopy(current_))
                #
                _key: List[str] = state._key.visit(key, value.bound, state)
                if isinstance(current_, IndexedLattice):
                    if isinstance(expr.typ.val_typ, DictLyraType):
                        itv_ = current_.summarize(keys=expr.typ.val_typ.key_typ)
                    else:
                        itv_ = current_.summarize()
                else:
                    itv_ = deepcopy(current_)
                if len(_key) == 1 and _key[0] != value.default:
                    value[_key[0]] = itv_
                else:
                    value[value.default] = itv_
            evaluated[KeysIdentifier(expr)] = _value
            evaluated[expr] = value
            evaluated[ValuesIdentifier(expr)] = value_
            evaluated[LengthIdentifier(expr)] = IntervalLattice(len(expr.keys), len(expr.keys))
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: 'Subscription', state=None, evaluation=None):
            def do(lattice, typ, key, current: Lattice) -> Lattice:
                updated: Lattice = current
                simple = (BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType)
                if isinstance(typ, simple):
                    if hasattr(lattice, 'from_literal'):
                        literal = Literal(typ, key)
                        updated = updated.join(lattice.from_literal(literal))
                    else:
                        updated = updated.join(lattice().top())
                else:
                    assert isinstance(typ, TupleLyraType)
                    val = literal_eval(key)
                    for i, subtyp in enumerate(typ.typs):
                        updated = do(lattice, subtyp, val[i], updated)
                return updated

            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target, state, evaluation)  # evaluate target
            if state.is_bottom():
                return evaluation
            target: IndexedLattice = evaluated[expr.target]
            assert isinstance(target, IndexedLattice)
            evaluated = self.visit(expr.key, state, evaluated)      # evaluate key
            if state.is_bottom():
                return evaluation
            key = evaluated[expr.key]
            _key: List[str] = state._key.visit(expr.key, target.bound, state)
            fetched = target.weak_get(_key)
            assert not isinstance(fetched, IndexedLattice)
            if fetched.is_bottom():  # key does not belong to target keys
                state.bottom()
                return evaluation
            if isinstance(expr.target.typ, SequenceLyraType):
                # check (and modify) target length based on key
                if isinstance(key, IntervalLattice):
                    length: IntervalLattice = evaluated[LengthIdentifier(expr.target)]
                    if 0 <= key.lower:  # key is positive
                        if length.upper <= key.lower:  # key is larger than length
                            state.bottom()
                            return evaluation
                        lower = IntervalLattice(lower=key.lower + 1)
                        if isinstance(expr.target, VariableIdentifier):
                            state.lengths[expr.target.length] = length.meet(lower)
                    elif key.upper < 0:  # key is negative
                        if length.upper + key.upper < 0:  # key is smaller than length
                            state.bottom()
                            return evaluation
                        upper = IntervalLattice(lower=-key.upper)
                        if isinstance(expr.target, VariableIdentifier):
                            state.lengths[expr.target.length] = length.meet(upper)
                # return value of key in target
                if isinstance(expr.typ, (SequenceLyraType, DictLyraType)):
                    index = {'_': fetched}
                    idxd = state.lattices[expr.typ](**state.arguments[expr.typ], index=index)
                    evaluated[expr] = idxd
                else:
                    evaluated[expr] = fetched
                if isinstance(expr.typ, (StringLyraType, ContainerLyraType)):
                    if isinstance(expr.target.typ, StringLyraType):
                        evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=1, upper=1)
                    else:
                        evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
                        if isinstance(expr.typ, DictLyraType):
                            _ktyp = expr.typ.key_typ
                            if isinstance(_ktyp, SequenceLyraType):
                                _kdx = {'_': deepcopy(fetched)}
                                _kdxd = state.lattices[_ktyp](**state.arguments[_ktyp], index=_kdx)
                                evaluated[KeysIdentifier(expr)] = _kdxd
                            else:
                                evaluated[KeysIdentifier(expr)] = deepcopy(fetched)
                            _vtyp = expr.typ.val_typ
                            if isinstance(_vtyp, (SequenceLyraType, DictLyraType)):
                                _vdx = {'_': deepcopy(fetched)}
                                _vdxd = state.lattices[_vtyp](**state.arguments[_vtyp], index=_vdx)
                                evaluated[ValuesIdentifier(expr)] = _vdxd
                            else:
                                evaluated[ValuesIdentifier(expr)] = deepcopy(fetched)
            else:
                assert isinstance(expr.target.typ, DictLyraType)
                keys = evaluated[KeysIdentifier(expr.target)]
                values = evaluated[ValuesIdentifier(expr.target)]
                # check (and modify) target length based on key
                intersection = deepcopy(key).meet(deepcopy(keys))
                if intersection.is_bottom():  # key does not belong to target keys
                    state.bottom()
                    return evaluation
                if isinstance(expr.target, VariableIdentifier):
                    length: IntervalLattice = state.lengths[expr.target.length]
                    state.lengths[expr.target.length] = length.meet(IntervalLattice(lower=1))
                # return value of key in target (refined with value of target values)
                if isinstance(expr.typ, (SequenceLyraType, DictLyraType)):
                    assert isinstance(values, IndexedLattice)
                    evaluated[expr] = deepcopy(values).refine(deepcopy(fetched))
                else:
                    evaluated[expr] = deepcopy(fetched).meet(deepcopy(values))
                if isinstance(expr.typ, (StringLyraType, ContainerLyraType)):
                    if isinstance(values, IndexedLattice) and values.default not in values.used:
                        length = IntervalLattice(lower=values.size, upper=values.size)
                        evaluated[LengthIdentifier(expr)] = length
                    else:
                        evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
                    if isinstance(expr.typ, DictLyraType):
                        assert isinstance(values, IndexedLattice)
                        _ktyp = expr.typ.key_typ
                        if isinstance(_ktyp, SequenceLyraType):
                            # TODO: we can do better if the used keys are precisely represented
                            _keys = evaluated[expr].summarize(keys=_ktyp, values=False)
                            _kdx = {'_': _keys}
                            _kdxd = state.lattices[_ktyp](**state.arguments[_ktyp], index=_kdx)
                            evaluated[KeysIdentifier(expr)] = _kdxd
                        else:
                            _keys = evaluated[expr].summarize(keys=_ktyp, values=False)
                            evaluated[KeysIdentifier(expr)] = deepcopy(fetched).meet(_keys)
                        _vtyp = expr.typ.val_typ
                        if isinstance(_vtyp, (SequenceLyraType, DictLyraType)):
                            evaluated[ValuesIdentifier(expr)] = evaluated[expr].summarize()
                        else:
                            values_ = evaluated[expr].summarize(keys=_ktyp)
                            evaluated[ValuesIdentifier(expr)] = deepcopy(fetched).meet(values_)
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: 'Slicing', state=None, evaluation=None):
            raise NotImplementedError   # TODO

        @copy_docstring(ExpressionVisitor.visit_Keys)
        def visit_Keys(self, expr: Keys, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target_dict, state, evaluation)
            if state.is_bottom():
                return evaluation
            assert isinstance(expr.typ, SetLyraType)
            keys = evaluated[KeysIdentifier(expr.target_dict)]
            if isinstance(keys, IndexedLattice):
                evaluated[expr] = keys.summarize()
                if keys.default not in keys.used:
                    length = IntervalLattice(lower=keys.size, upper=keys.size)
                    evaluated[LengthIdentifier(expr)] = length
                else:
                    evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            else:
                evaluated[expr] = deepcopy(keys)
                evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_Values)
        def visit_Values(self, expr: Values, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target_dict, state, evaluation)
            if state.is_bottom():
                return evaluation
            values = evaluated[ValuesIdentifier(expr.target_dict)]
            assert isinstance(expr.typ, SetLyraType)
            if isinstance(values, IndexedLattice):
                evaluated[expr] = values.summarize()
                if values.default not in values.used:
                    length = IntervalLattice(lower=values.size, upper=values.size)
                    evaluated[LengthIdentifier(expr)] = length
                else:
                    evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            else:
                evaluated[expr] = deepcopy(values)
                evaluated[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            return evaluated

        @copy_docstring(ExpressionVisitor.visit_CastOperation)
        def visit_CastOperation(self, expr: CastOperation, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if state.is_bottom():
                return evaluation
            iscontainer = isinstance(expr.expression.typ, (SequenceLyraType, ContainerLyraType))
            isstring = isinstance(expr.expression.typ, StringLyraType)
            isset = isinstance(expr.expression.typ, SetLyraType)
            isdictionary = isinstance(expr.expression.typ, DictLyraType)
            if isinstance(expr.typ, BooleanLyraType) and iscontainer:
                current: IndexedLattice = evaluated[expr.expression]
                if current.is_empty():
                    value = state.lattices[expr.typ](**state.arguments[expr.typ]).false()
                elif current.is_nonempty():
                    value = state.lattices[expr.typ](**state.arguments[expr.typ]).true()
                else:
                    value = state.lattices[expr.typ](**state.arguments[expr.typ]).maybe()
                evaluation[expr] = value
            elif isinstance(expr.typ, (IntegerLyraType, FloatLyraType)) and isstring:
                current: IndexedLattice = evaluated[expr.expression]
                evaluation[expr] = current.summarize()
            elif isinstance(expr.typ, StringLyraType):
                value = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                evaluation[expr] = value
                evaluation[LengthIdentifier(expr)] = IntervalLattice(lower=0)
            elif isinstance(expr.typ, (ListLyraType, TupleLyraType)) and isset:
                current = deepcopy(evaluated[expr.expression])
                assert not isinstance(current, IndexedLattice)
                indexed = {'_': current}
                value = state.lattices[expr.typ](**state.arguments[expr.typ], index=indexed)
                evaluation[expr] = value
                evaluation[LengthIdentifier(expr)] = evaluation[LengthIdentifier(expr.expression)]
            elif isinstance(expr.typ, (ListLyraType, TupleLyraType)) and isdictionary:
                current = deepcopy(evaluated[KeysIdentifier(expr.expression)])
                if isinstance(current, IndexedLattice):
                    evaluation[expr] = current
                else:
                    indexed = {'_': current}
                    value = state.lattices[expr.typ](**state.arguments[expr.typ], index=indexed)
                    evaluation[expr] = value
                evaluation[LengthIdentifier(expr)] = evaluation[LengthIdentifier(expr.expression)]
            elif isinstance(expr.typ, SetLyraType) and isdictionary:
                current = evaluated[KeysIdentifier(expr.expression)]
                if isinstance(current, IndexedLattice):
                    evaluation[expr] = current.summarize()
                else:
                    evaluation[expr] = deepcopy(current)
                evaluation[LengthIdentifier(expr)] = evaluation[LengthIdentifier(expr.expression)]
            else:  # default case
                expr = evaluated[expr.expression]
                itv = expr.summarize() if isinstance(expr, IndexedLattice) else deepcopy(expr)
                evaluation[expr] = deepcopy(expr)
                if isinstance(expr.typ, (SequenceLyraType, ContainerLyraType)):
                    default: IntervalLattice = IntervalLattice(lower=0)
                    length = evaluation.get(LengthIdentifier(expr.expression), default)
                    evaluation[LengthIdentifier(expr)] = length
                    if isinstance(expr.typ, DictLyraType):
                        if isinstance(expr.typ.key_typ, SequenceLyraType):
                            _kidx = {'_': deepcopy(itv)}
                            _ktyp = expr.typ.key_typ
                            value = state.lattices[_ktyp](**state.arguments[_ktyp], index=_kidx)
                            evaluation[KeysIdentifier(expr)] = value
                        else:
                            evaluation[KeysIdentifier(expr)] = deepcopy(itv)
                        if isinstance(expr.typ.val_typ, (SequenceLyraType, DictLyraType)):
                            _vidx = {'_': deepcopy(itv)}
                            _vtyp = expr.typ.val_typ
                            value = state.lattices[_vtyp](** state.arguments[_vtyp], index=_vidx)
                            evaluation[ValuesIdentifier(expr)] = value
                        else:
                            evaluation[ValuesIdentifier(expr)] = deepcopy(itv)
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
        def visit_BinarySequenceOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            if state.is_bottom():
                return evaluation
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if state.is_bottom():
                return evaluation
            value1 = evaluated2[expr.left]
            len1 = evaluated2[LengthIdentifier(expr.left)]
            value2 = evaluated2[expr.right]
            len2 = evaluated2[LengthIdentifier(expr.right)]
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                if isinstance(value1, SequenceMixin):
                    evaluated2[expr] = deepcopy(value1).concat(value2)
                    evaluated2[LengthIdentifier(expr)] = deepcopy(len1).add(deepcopy(len2))
                else:
                    evaluated2[expr] = state.lattices[expr.typ](**state.arguments[expr.typ]).top()
                    evaluated2[LengthIdentifier(expr)] = IntervalLattice(lower=0)
                return evaluated2
            raise ValueError(f"Binary sequence operator '{str(expr.operator)}' is unsupported!")

    _evaluation = ExpressionEvaluation()

    # expression refinement

    class ExpressionRefinement(Basis.ExpressionRefinement):

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            state.store[expr] = refined
            if expr.is_dictionary:
                # _refined = evaluation[expr.keys].meet(value)
                # state.keys[expr.keys] = _refined
                summary = refined.summarize()
                if isinstance(state.values[expr.values], IndexedLattice):
                    state.values[expr.values] = evaluation[expr.values].refine(summary)
                else:
                    state.values[expr.values] = evaluation[expr.values].meet(summary)
            return state

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, evaluation=None, value=None, state=None):
            if isinstance(value, IndexedLattice):
                refined = evaluation[expr].meet(value)
            else:
                refined = evaluation[expr].refine(value)
            updated = state
            for idx, item in enumerate(expr.items):
                if isinstance(refined, IndexedLattice):
                    updated = self.visit(item, evaluation, deepcopy(refined[str(idx)]), updated)
                else:
                    updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, evaluation=None, value=None, state=None):
            if isinstance(value, IndexedLattice):
                refined = evaluation[expr].meet(value)
            else:
                refined = evaluation[expr].refine(value)
            updated = state
            for idx, item in enumerate(expr.items):
                if isinstance(refined, IndexedLattice):
                    updated = self.visit(item, evaluation, deepcopy(refined[str(idx)]), updated)
                else:
                    updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, evaluation=None, value=None, state=None):
            if isinstance(value, IndexedLattice):
                refined = evaluation[expr].meet(value)
            else:
                refined = evaluation[expr].refine(value)
            updated = state
            for idx, item in enumerate(expr.items):
                if isinstance(refined, IndexedLattice):
                    updated = self.visit(item, evaluation, deepcopy(refined[str(idx)]), updated)
                else:
                    updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, evaluation=None, value=None, state=None):
            if isinstance(value, IndexedLattice):
                refined = evaluation[expr].meet(value)
            else:
                refined = evaluation[expr].refine(value)
            updated = state
            for key, val in zip(expr.keys, expr.values):
                updated = self.visit(val, evaluation, deepcopy(refined[str(key)]), updated)
            return updated

        def visit_Subscription(self, expr, evaluation=None, value=None, state=None):
            refined = deepcopy(evaluation[expr]).meet(value)
            target: IndexedLattice = deepcopy(evaluation[expr.target])          # value of target
            _key: List[str] = state._key.visit(expr.key, target.bound, state)   # value of key
            updated = state
            # refine value of target
            itv = refined.summarize() if isinstance(refined, IndexedLattice) else refined
            if len(_key) == 1 and _key[0] != target.default:    # key is precise
                target[_key[0]] = itv
            else:
                target.weak_set(_key, itv)
            updated = self.visit(expr.target, evaluation, target, updated)
            key = evaluation[expr.key]
            if isinstance(expr.target.typ, SequenceLyraType):
                if isinstance(key, IntervalLattice):
                    length: IntervalLattice = evaluation[LengthIdentifier(expr.target)]
                    if 0 <= key.lower:  # key is positive
                        lower = IntervalLattice(lower=key.lower + 1)
                        if isinstance(expr.target, VariableIdentifier):
                            updated.lengths[expr.target.length] = length.meet(lower)
                    elif key.upper < 0:  # key is negative
                        upper = IntervalLattice(lower=-key.upper)
                        if isinstance(expr.target, VariableIdentifier):
                            updated.lengths[expr.target.length] = length.meet(upper)
            else:
                assert isinstance(expr.target.typ, DictLyraType)
                if isinstance(expr.target, VariableIdentifier):
                    length: IntervalLattice = state.lengths[expr.target.length]
                    state.lengths[expr.target.length] = length.meet(IntervalLattice(lower=1))
            # refine value of key
            if isinstance(expr.target.typ, SequenceLyraType):
                _typ = IntegerLyraType()    # the key type must be IntegerLyraType
            else:
                assert isinstance(expr.target.typ, DictLyraType)
                _typ = expr.target.typ.key_typ
            instance = state.lattices[_typ](**state.arguments[_typ])
            reversed = evaluation[expr.target].reverse(instance, _typ, itv)
            updated = self.visit(expr.key, evaluation, reversed, updated)
            return updated

        def visit_Slicing(self, expr: 'Slicing', evaluation=None, value=None, state=None):
            raise NotImplementedError  # TODO

        @copy_docstring(ExpressionVisitor.visit_CastOperation)
        def visit_CastOperation(self, expr, evaluation=None, value=None, state=None):
            raise NotImplementedError  # TODO

    _refinement = ExpressionRefinement()
