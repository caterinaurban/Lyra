"""
Assumption Domain
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from typing import List

from copy import deepcopy

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.abstract_domains.quality.assumption_lattice import TypeLattice, AssumptionLattice, \
    InputAssumptionLattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import Expression, VariableIdentifier, ExpressionVisitor, \
    BinaryComparisonOperation
from lyra.core.statements import Call, LiteralEvaluation
from lyra.core.types import ListLyraType, IntegerLyraType, BooleanLyraType, FloatLyraType, \
    StringLyraType
from lyra.core.utils import copy_docstring


class InputAssumptionStack(Stack):
    """ Input Assumption Stack

    Stack of elements from the Input Assumption Lattice.

    """

    def __init__(self):
        super().__init__(InputAssumptionLattice, {})

    @copy_docstring(Stack.pop)
    def pop(self):
        if len(self.stack) > 1:
            element = self.stack.pop()
            if len(element.assmps) > 0:
                if element.is_loop:
                    num_iter = self.get_num_iter_from_condition(element.condition)
                    if num_iter is None:
                        self.lattice.top()
                    else:
                        self.stack[-1].add_assumptions_with_iter(num_iter, element.assmps)
                else:
                    self.stack[-1].add_assumptions_front(element.assmps)

    def get_num_iter_from_condition(self, condition):
        """Extracts the number of iterations from a condition"""
        if isinstance(condition, BinaryComparisonOperation):
            if condition.operator == BinaryComparisonOperation.Operator.In:
                in_element = condition.right
                if isinstance(in_element, Call) and in_element.name == "range":
                    if len(in_element.arguments) == 1:
                        num_iter = in_element.arguments[0]
                        if isinstance(num_iter, LiteralEvaluation):
                            return int(num_iter.literal.val)
        return None

    @copy_docstring(Stack.push)
    def push(self):
        self.stack.append(InputAssumptionLattice())


class AssumptionState(Store, State):
    """Assumption analysis state. An element of the assumption abstract domain.

    Map from each program variable to the assumption tuple representing its current assumptions.

    .. document private methods
    .. automethod:: AssumptionState._assign
    .. automethod:: AssumptionState._assume
    .. automethod:: AssumptionState._output
    .. automethod:: AssumptionState._substitute

    """

    def __init__(self, variables: List[VariableIdentifier]):
        types = [BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType, ListLyraType]
        lattices = {typ: AssumptionLattice for typ in types}
        super().__init__(variables, lattices)
        self.store[self.input_var] = InputAssumptionStack()

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        error = 'AssumptionState for forward assign statement analysis is not supported!'
        raise NotImplementedError(error)

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'AssumptionState':
        self.current_stack_top.condition = condition
        curr_condition = condition
        self._assume_range(curr_condition)
        self._refinement.visit(condition, None, self)
        return self

    def _assume_range(self, condition: Expression) -> 'AssumptionState':
        """
        Executes assume for the range assumption
        """
        interval_state = self.assmp_to_interval_state()
        res = interval_state.assume({condition})
        self.interval_to_assmp_state(res)
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'AssumptionState':
        self.store[self.input_var].push()
        return self

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'AssumptionState':
        self.store[self.input_var].pop()
        return self

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'AssumptionState':
        self.store[self.input_var].push()
        self.current_stack_top.is_loop = True
        return self

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'AssumptionState':
        self.store[self.input_var].pop()
        return self

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'AssumptionState':
        return self._refinement.visit(output, AssumptionLattice(), self)

    @copy_docstring(State._raise_error)
    def _raise_error(self) -> 'AssumptionState':
        return self.bottom()

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'AssumptionState':
        if isinstance(left, VariableIdentifier):
            assumption = deepcopy(self.store[left])
            assumptions_range = self._substitute_range(left, right)
            assumptions_range_left = deepcopy(assumptions_range.store[left].range_assumption)
            self.store[left].top()
            self._refinement.visit(right, assumption, self)
            self.store[left].range_assumption.meet(assumptions_range_left)
            return self
        error = f'Substitution for {left} not yet implemented!'
        raise NotImplementedError(error)

    def _substitute_range(self, left: Expression, right: Expression) -> 'AssumptionState':
        """
        Executes substitute for the range assumption
        """
        interval_state = self.assmp_to_interval_state()
        res = interval_state.substitute({left}, {right})
        return self.interval_to_assmp_state(res)

    @property
    def input_var(self):
        return VariableIdentifier(StringLyraType(), '.IN')

    @property
    def current_stack_top(self):
        return self.store[self.input_var].stack[-1]

    def assmp_to_interval_state(self):
        """
        Turns the current AssumptionState into an IntervalState
        """
        variables = [v for v in self.variables if isinstance(v.typ, FloatLyraType)
                     or isinstance(v.typ, IntegerLyraType) or isinstance(v.typ, BooleanLyraType)]
        interval_state = IntervalState(variables)
        assumptions = [(k, v) for (k, v) in self.store.items() if isinstance(v, AssumptionLattice)]
        for var, assmp in assumptions:
            interval_state.store[var] = deepcopy(assmp.range_assumption)
        return interval_state

    def interval_to_assmp_state(self, interval_state: IntervalState):
        """
        Overwrites information of the current store with information from the interval state
        """
        for var, interval in interval_state.store.items():
            type_assumption = self.store[var].type_assumption
            self.store[var] = AssumptionLattice(type_assumption, interval)
        return self

    class AssumptionRefinement(ExpressionVisitor):
        def visit_Subscription(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_Literal(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_Slicing(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_Call(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_BinaryBooleanOperation(self, expr, assumption=None, state=None):
            left = self.visit(expr.left, AssumptionLattice(), state)
            right = self.visit(expr.right, AssumptionLattice(), left)
            return right

        def visit_UnaryArithmeticOperation(self, expr, assumption=None, state=None):
            expr_type = TypeLattice.from_lyra_type(expr.typ)
            refined = AssumptionLattice(expr_type.meet(assumption.type_assumption))
            return self.visit(expr.expression, refined, state)

        def visit_BinaryArithmeticOperation(self, expr, assumption=None, state=None):
            expr_type = TypeLattice.from_lyra_type(expr.typ)
            refined = AssumptionLattice(expr_type.meet(assumption.type_assumption))
            left = self.visit(expr.left, refined, state)
            right = self.visit(expr.right, refined, left)
            return right

        def visit_BinaryComparisonOperation(self, expr, assumption=None, state=None):
            left = self.visit(expr.left, AssumptionLattice(), state)
            right = self.visit(expr.right, AssumptionLattice(), left)
            return right

        def visit_AttributeReference(self, expr, assumption=None, state=None):
            error = f'Refinement for a {expr.__class__.__name__} is not supported!'
            raise NotImplementedError(error)

        def visit_Input(self, expr, assumption=None, state=None):
            type_assumption = TypeLattice.from_lyra_type(expr.typ)
            input_assumption = AssumptionLattice(type_assumption).meet(assumption)
            if state.store[state.input_var].lattice.is_top():
                state.current_stack_top.meet(InputAssumptionLattice())
            state.store[state.input_var].lattice.add_assumption_front(input_assumption)
            return state

        def visit_ListDisplay(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_UnaryBooleanOperation(self, expr, assumption=None, state=None):
            return self.visit(expr.expression, TypeLattice(), state)

        def visit_VariableIdentifier(self, expr, assumption=None, state=None):
            state.store[expr].meet(assumption)
            expr_type = TypeLattice.from_lyra_type(expr.typ)
            state.store[expr].type_assumption.meet(expr_type)
            return state

        def visit_LengthIdentifier(self, expr, assumption=None, state=None):
            return state

    _refinement = AssumptionRefinement()
