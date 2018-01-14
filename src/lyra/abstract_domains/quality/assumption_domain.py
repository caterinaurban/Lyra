"""
Assumption Domain
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from typing import List

from copy import deepcopy

import math

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.abstract_domains.quality.assumption_lattice import TypeLattice, AssumptionLattice, \
    InputAssumptionLattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import Expression, VariableIdentifier, ExpressionVisitor, \
    BinaryComparisonOperation, Literal, Range, UnaryArithmeticOperation
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
            if element.infoloss:
                self.lattice.assmps.clear()
                self.lattice.infoloss = True
            elif element.is_loop:
                if len(element.assmps) > 0:
                    num_iter = self.get_num_iter_from_condition(element.condition)
                    if num_iter is None:
                        self.lattice.assmps.clear()
                        self.lattice.infoloss = True
                        return
                    if self.check_second_iteration(element):
                        self.lattice.assmps.pop(0)
                    pp = element.assmps[0].pp
                    self.lattice.add_assmps_with_iter(num_iter, element.assmps, pp)
                    self.lattice.join_as_loop = True
                else:
                    self.lattice.join_as_loop = True
            elif len(element.assmps) > 0:
                self.lattice.add_assumptions_front(element.assmps)
                self.lattice.join_as_loop = False

    def check_second_iteration(self, element):
        """Checks if the assumption in front of the current stack top is from the same program
        point than the front assumption of the element that we pop.

        :param element: The element that is currently popped
        :return: f the assumption in front of the current stack top is from the same program
        point than the parameter element.
        """
        if len(self.lattice.assmps) == 0:
            return False
        prev_element = self.lattice.assmps[0]
        if not isinstance(prev_element, InputAssumptionLattice):
            return False
        return prev_element.pp == element.assmps[0].pp

    def get_num_iter_from_condition(self, condition):
        """Extracts the number of iterations from a condition

        :param condition: condition to analyze for number of iterations
        :return: number of iterations if possible, otherwise None
        """
        if isinstance(condition, BinaryComparisonOperation):
            if condition.operator == BinaryComparisonOperation.Operator.In:
                in_element = condition.right
                if isinstance(in_element, Range):
                    start = self.get_value_for_iteration(in_element.start)
                    end = self.get_value_for_iteration(in_element.end)
                    step = self.get_value_for_iteration(in_element.step)
                    if start is not None and end is not None and step is not None:
                        return math.ceil((end - start) / step)
                    error = f"Analysis of range() is only implemented for Literal arguments."
                    raise NotImplementedError(error)
        return None

    def get_value_for_iteration(self, iter_expr):
        """Gets the value from an expression. Works for Literals or UnaryOperations of a Literal.

        :param iter_expr: expression to extract the value from
        :return: The value of the evaluated expression or None
        """
        if isinstance(iter_expr, Literal):
            return int(iter_expr.val)
        elif isinstance(iter_expr, UnaryArithmeticOperation):
            is_minus = iter_expr.operator == UnaryArithmeticOperation.Operator.Sub
            if isinstance(iter_expr.expression, Literal):
                val = int(iter_expr.expression.val)
                if is_minus:
                    val = -val
                return val
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
        self.store[self.input_var].lattice.is_main = True
        interval_vars = [v for v in variables if not isinstance(v.typ, StringLyraType)]
        self.store[self.relationship] = IntervalState(interval_vars)

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        error = 'AssumptionState for forward assign statement analysis is not supported!'
        raise NotImplementedError(error)

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'AssumptionState':
        self.current_stack_top.condition = condition
        curr_condition = condition
        self._assume_range(curr_condition)
        self._refinement.visit(condition, AssumptionLattice(), self)
        return self

    def _assume_range(self, condition: Expression) -> 'AssumptionState':
        """
        Executes assume for the range assumption
        """
        res = self.store[self.relationship].assume({condition})
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

    @copy_docstring(State.raise_error)
    def raise_error(self) -> 'AssumptionState':
        return self.bottom()

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'AssumptionState':
        if isinstance(left, VariableIdentifier):
            assumptions = deepcopy(self.store[left])
            assumption = InputAssumptionLattice(1, assumptions)
            #assumption = deepcopy(self.store[left])
            assumption.var_name = left
            assumption.relations = deepcopy(self.store[self.relationship])
            num_in_elements = len(self.store[self.input_var].lattice.assmps)
            assumption.input_info = {left: num_in_elements}

            self.substitute_range(left, right)
            self.substitute_range_in_assmps(left, right, self.current_stack_top.assmps)

            self.store[left].top()
            self._refinement.visit(right, assumption, self)
            return self
        error = f'Substitution for {left} not yet implemented!'
        raise NotImplementedError(error)

    def substitute_range(self, left: Expression, right: Expression) -> 'AssumptionState':
        """Executes substitute for the range assumption

        :param left: left hand side expression
        :param right: right hand side expression
        :return: state after substitution of the ranges
        """
        res = self.store[self.relationship].substitute({left}, {right})
        return self.interval_to_assmp_state(res)

    def substitute_range_in_assmps(self, left, right, assmps) -> 'AssumptionState':
        for assumption in assmps:
            if isinstance(assumption, AssumptionLattice):
                if assumption.var_name != left:
                    assumption.relations.substitute({left}, {right})
            else:
                self.substitute_range_in_assmps(left, right, assumption.assmps)
        return self

    @property
    def input_var(self):
        return VariableIdentifier(StringLyraType(), '.IN')

    @property
    def relationship(self):
        return VariableIdentifier(StringLyraType(), '.REL')

    @property
    def current_stack_top(self):
        return self.store[self.input_var].lattice

    def interval_to_assmp_state(self, interval_state: IntervalState):
        """
        Overwrites information of the current store with information from the interval state
        """
        for var, interval in interval_state.store.items():
            type_assumption = self.store[var].type_assumption
            self.store[var] = AssumptionLattice(type_assumption)
        return self

    class AssumptionRefinement(ExpressionVisitor):
        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, assumption=None, state=None):
            left = self.visit(expr.left, AssumptionLattice(), state)
            right = self.visit(expr.right, AssumptionLattice(), left)
            return right

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, assumption=None, state=None):
            expr_type = TypeLattice.from_lyra_type(expr.typ)
            refined = AssumptionLattice(expr_type.meet(assumption.type_assumption))
            return self.visit(expr.expression, refined, state)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, assumption=None, state=None):
            expr_type = TypeLattice.from_lyra_type(expr.typ)
            refined = AssumptionLattice(expr_type.meet(assumption.type_assumption))
            left = self.visit(expr.left, refined, state)
            right = self.visit(expr.right, refined, left)
            return right

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, assumption=None, state=None):
            left = self.visit(expr.left, AssumptionLattice(), state)
            right = self.visit(expr.right, AssumptionLattice(), left)
            return right

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr, assumption=None, state=None):
            error = f'Refinement for a {expr.__class__.__name__} is not supported!'
            raise NotImplementedError(error)

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr, assumption=None, state=None):
            type_assmp = TypeLattice.from_lyra_type(expr.typ)
            #var_name = assumption.var_name
            #rel = assumption.relations
            #num_in_elements = len(state.store[state.input_var].lattice.assmps)
            #in_info = {assumption.var_name: num_in_elements}
            #input_assmp = AssumptionLattice(type_assmp, var_name, rel, in_info).meet(assumption)
            assumption.assmps.type_assumption.meet(type_assmp)
            assumption.pp = state.pp
            if state.store[state.input_var].lattice.infoloss:
                if len(state.store[state.input_var].stack) == 1:
                    state.store[state.input_var].lattice.infoloss = False
            state.store[state.input_var].lattice.add_assumption_front(assumption)
            return state

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, assumption=None, state=None):
            return self.visit(expr.expression, TypeLattice(), state)

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, assumption=None, state=None):
            state.store[expr].type_assumption.meet(assumption.type_assumption)
            expr_type = TypeLattice.from_lyra_type(expr.typ)
            state.store[expr].type_assumption.meet(expr_type)
            return state

    _refinement = AssumptionRefinement()
