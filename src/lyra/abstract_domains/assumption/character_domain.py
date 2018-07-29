import string
from copy import deepcopy
from typing import Set, List, Dict, Union, Tuple

from lyra.abstract_domains.assumption.assumption_domain import InputMixin, JSONMixin
from lyra.abstract_domains.lattice import BottomMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.assumption.error import CheckerError, DependencyError
from lyra.core.expressions import Expression, VariableIdentifier, ExpressionVisitor, BinaryComparisonOperation
from lyra.core.expressions import Literal, BinaryArithmeticOperation, UnaryBooleanOperation, BinaryBooleanOperation
from lyra.core.types import StringLyraType

_alphabet = set(string.printable)


class CharacterLattice(BottomMixin, JSONMixin):

    def to_json(self) -> dict:
        js = {
            'maybe': list(self.certainly),
            'certainly': list(self.maybe)
        }
        return js

    @staticmethod
    def from_json(json: dict) -> 'JSONMixin':
        return CharacterLattice(set(json['maybe']), set(json['certainly']))

    def check_input(self,  pp: VariableIdentifier, pp_value: Dict[str, Union[Tuple[int, ...], CheckerError]], line_errors: Dict[int, List[CheckerError]]):
        if self.is_top():
            return
        input_line = pp_value[pp][0]
        input_value = pp_value[pp][1]
        if input_value is not None:
            input_value = set(input_value)
            error_message = ""
            if not input_value.issuperset(self.certainly):
                error_message += "String must contain all characters: {}; ".format(self.certainly)

            if not input_value.issubset(self.maybe):
                error_message += "String must contain only characters: {}".format(self.maybe)
            if len(error_message) > 0:
                error = CheckerError(error_message)
                line_errors[input_line].append(error)
        else:
            error = DependencyError(input_line)
            line_errors[input_line].append(error)

    def __init__(self, certainly=set(), maybe=_alphabet):
        self._certainly = certainly
        self._maybe = maybe
        super().__init__()
        if not self.certainly.issubset(self.maybe):
            self.bottom()

    @property
    def certainly(self):
        return self._certainly

    @property
    def maybe(self):
        return self._maybe

    def top(self):
        return self._replace(CharacterLattice())

    def __repr__(self):
        if self.is_bottom():
            return "⊥"

        if self.is_top():
            return "T"

        return "({}, {})".format(self.certainly, self.maybe)

    def is_top(self) -> bool:
        return not self.is_bottom() and self.certainly == set() and self.maybe == _alphabet

    def _less_equal(self, other: 'CharacterLattice') -> bool:
        return self.maybe.issuperset(other.maybe) and self.certainly.issubset(other.certainly)

    def _join(self, other: 'CharacterLattice') -> 'CharacterLattice':
        maybe = self.certainly.intersection(other.certainly)
        certainly = self.maybe.intersection(other.maybe)
        return self._replace(CharacterLattice(maybe, certainly))

    def _meet(self, other: 'CharacterLattice'):
        maybe = self.certainly.union(other.certainly)
        certainly = self.maybe.intersection(other.maybe)
        return self._replace(CharacterLattice(maybe, certainly))

    def _widening(self, other: 'CharacterLattice'):
        return self._join(other)

    def concat(self, other: 'CharacterLattice') -> 'CharacterLattice':
        return self._replace(CharacterLattice(self.certainly.union(other.certainly), self.maybe.union(other.maybe)))


class ConditionEvaluator(ExpressionVisitor):

    def visit_Literal(self, expr: 'Literal', state=None, eval=None):
        if expr.typ == StringLyraType():
            return CharacterLattice(set(expr.val), set(expr.val))
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_Input(self, expr: 'Input', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_VariableIdentifier(self, expr: 'VariableIdentifier', state=None, eval=None):
        return state.store[expr]

    def visit_ListDisplay(self, expr: 'ListDisplay', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_Range(self, expr: 'Range', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_AttributeReference(self, expr: 'AttributeReference', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_Subscription(self, expr: 'Subscription', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_Slicing(self, expr: 'Slicing', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation', state=None, eval=None):
        if expr.operator == BinaryArithmeticOperation.Operator.Add:
            left = self.visit(expr.left, state, eval)
            right = self.visit(expr.right, state, eval)
            return left.concat(right)
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))

    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation', state=None, eval=None):
        raise NotImplementedError("Condition evalutator not supported for {}".format(expr))


class Refinement(ExpressionVisitor):

    def visit_Literal(self, expr: 'Literal', state=None, evaluation=None):
        pass

    def visit_Input(self, expr: 'Input', state=None, evaluation=None):
        # print("BEFORE REC CHAR", type(state).inputs)
        state.record(deepcopy(evaluation))

    def visit_VariableIdentifier(self, expr: 'VariableIdentifier', state=None, evaluation=None):
        state.store[expr].meet(evaluation)

    def visit_ListDisplay(self, expr: 'ListDisplay', state=None, evaluation=None):
        pass

    def visit_Range(self, expr: 'Range', state=None, evaluation=None):
        pass

    def visit_AttributeReference(self, expr: 'AttributeReference', state=None, evaluation=None):
        pass

    def visit_Subscription(self, expr: 'Subscription', state=None, evaluation=None):
        pass

    def visit_Slicing(self, expr: 'Slicing', state=None, evaluation=None):
        pass

    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation', state=None, evaluation=None):
        pass

    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', state=None, evaluation=None):
        pass

    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation', state=None, evaluation=None):
        evaluation = CharacterLattice(maybe=evaluation.certainly)
        self.visit(expr.right, state, evaluation)
        self.visit(expr.left, state, evaluation)

    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', state=None, evaluation=None):
        pass

    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation', state=None, evaluation=None):
        pass


_evaluator = ConditionEvaluator()
_refinement = Refinement()


class CharacterState(Store, InputMixin):

    def __init__(self, variables: Set[VariableIdentifier]):
        self._variables = variables
        lattices = {v.typ: CharacterLattice for v in variables}
        super().__init__(variables, lattices)

    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'InputMixin':
        return self

    def unify(self, other: 'InputMixin') -> 'InputMixin':
        return self

    def _assign(self, left: Expression, right: Expression) -> 'State':
        raise Exception("Assignment should not be called in backward analysis.")

    def _assume(self, condition: Expression) -> 'State':
        if isinstance(condition, UnaryBooleanOperation):
            if condition.operator == UnaryBooleanOperation.Operator.Neg:
                expression = condition.expression
                if isinstance(expression, BinaryComparisonOperation):
                    left = expression.left
                    operator = expression.operator.reverse_operator()
                    right = expression.right
                    return self._assume(BinaryBooleanOperation(expression.typ, left, operator, right))
                elif isinstance(expression, UnaryBooleanOperation):
                    if isinstance(expression, UnaryBooleanOperation.Operator.Neg):
                        return self._assume(expression.expression)
                elif isinstance(expression, BinaryBooleanOperation):
                    left = expression.left
                    left = UnaryBooleanOperation(left.typ, UnaryBooleanOperation.Operator.Neg, left)
                    operator = expression.operator.reverse_operator()
                    right = expression.right
                    right = UnaryBooleanOperation(right.typ, UnaryBooleanOperation.Operator.Neg, right)
                    return self._assume(BinaryBooleanOperation(expression.typ, left, operator, right))
        elif isinstance(condition, BinaryBooleanOperation):
            if condition.operator == BinaryBooleanOperation.Operator.And:
                right = deepcopy(self)._assume(condition.right)
                return self._assume(condition.left).meet(right)
            if condition.operator == BinaryBooleanOperation.Operator.Or:
                right = deepcopy(self)._assume(condition.right)
                return self._assume(condition.left).join(right)
        elif isinstance(condition, BinaryComparisonOperation):
            if condition.operator == BinaryComparisonOperation.Operator.Eq:
                left = condition.left
                right = condition.right
                try:
                    left_eval = _evaluator.visit(condition.left, self)
                    right_eval = _evaluator.visit(condition.right, self)
                except NotImplementedError:
                    return self.meet(deepcopy(self.top()))
                _refinement.visit(left, self, right_eval)
                _refinement.visit(right, self, left_eval)
        return self

    def enter_if(self) -> 'State':
        return self

    def exit_if(self) -> 'State':
        return self

    def enter_loop(self) -> 'State':
        return self

    def exit_loop(self) -> 'State':
        return self

    def _output(self, output: Expression) -> 'State':
        return self

    def _substitute(self, left: Expression, right: Expression) -> 'State':
        left_eval = _evaluator.visit(left, self)
        _refinement.visit(right, self, left_eval)
        self.store[left].top()
        # print("AFTER REC CHAR", type(self).inputs)
        return self
