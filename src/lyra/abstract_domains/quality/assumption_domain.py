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
    InputAssumptionLattice, MultiInputAssumptionLattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import Expression, VariableIdentifier, ExpressionVisitor, \
    BinaryComparisonOperation, Literal, Range, UnaryArithmeticOperation, LengthIdentifier, \
    UnaryBooleanOperation, Subscription
from lyra.core.types import ListLyraType, IntegerLyraType, BooleanLyraType, FloatLyraType, \
    StringLyraType
from lyra.core.utils import copy_docstring


class InputAssumptionStack(Stack):
    """ Input Assumption Stack

    Stack of elements from the Input Assumption Lattice.

    """

    def __init__(self):
        super().__init__(MultiInputAssumptionLattice, {})

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
                    self.lattice.add_assmps_with_iter(num_iter, element.assmps, element.pp)
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
        if not isinstance(prev_element, MultiInputAssumptionLattice):
            return False
        if prev_element.pp is None:
            return False
        return prev_element.pp == element.pp

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
        self.stack.append(MultiInputAssumptionLattice())


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
        interval_types = (BooleanLyraType, IntegerLyraType, FloatLyraType)
        interval_vars = [v for v in variables if isinstance(v.typ, interval_types)]
        self.store[self.relationship_var] = IntervalState(interval_vars)
        self.new_input = None

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        error = 'AssumptionState for forward assign statement analysis is not supported!'
        raise NotImplementedError(error)

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'AssumptionState':
        self.stack_top.condition = condition
        curr_condition = condition
        self.assume_relations(curr_condition)
        self._refinement.visit(condition, AssumptionLattice(), self)
        return self

    def assume_relations(self, condition: Expression):
        """Executes assume for the relations

        :param condition: condition to assume
        """
        if self.check_if_interval_support(condition):
            self.relationship_state.assume({condition})

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
        self.stack_top.is_loop = True
        return self

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'AssumptionState':
        self.stack_top.pp = self.pp
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
            relations_before = deepcopy(self.relationship_state)
            self.substitute_relations(left, right)
            assumption = deepcopy(self.store[left])
            self.store[left].top()
            self._refinement.visit(right, assumption, self)
            if self.new_input is not None:
                input_assmp = InputAssumptionLattice(assmp=self.new_input)
                input_assmp.var_name = left
                input_assmp.relations = relations_before
                input_assmp.input_info = {left: self.pp.line}
                input_assmp.pp = self.pp
                self.stack_top.add_assumption_front(input_assmp)
            self.substitute_input_assmps(left, right, self.stack_top.assmps)
            self.new_input = None
            return self
        #TODO
        #elif isinstance(left, Subscription):
        #    self._refinement.visit(left, AssumptionLattice(), self)
        #    self._refinement.visit(right, AssumptionLattice(), self)
        #    return self
        error = f'Substitution for {left} not yet implemented!'
        raise NotImplementedError(error)

    def substitute_relations(self, left: Expression, right: Expression):
        """Executes substitute for the relations

        :param left: left hand side expression
        :param right: right hand side expression
        """
        if self.check_if_interval_support(left) and self.check_if_interval_support(right):
            self.relationship_state.substitute({left}, {right})

    def substitute_input_assmps(self, left: VariableIdentifier, right: Expression, assmps):
        """Substitutes the variables used in the input assumption collection.

        :param left: left hand side expression
        :param right: right hand side expression
        :param assmps: current assumptions to substitute
        """
        for assumption in assmps:
            if isinstance(assumption, InputAssumptionLattice):
                if self.new_input is not None:
                    new_input_assmp = self.stack_top.assmps[0]
                    var_name = new_input_assmp.var_name
                    if var_name not in assumption.input_info:
                        input_index = new_input_assmp.input_info[var_name]
                        assumption.input_info[var_name] = input_index
                elif assumption.var_name is not None and assumption.var_name.name != left.name:
                    assumption.relations.substitute({left}, {right})
            else:
                self.substitute_input_assmps(left, right, assumption.assmps)

    def check_if_interval_support(self, expr):
        """Checks if the current expression is supported by the interval analysis.

        :param expr: current expression
        :return: True if the expression is supported by the interval analysis
        """
        if isinstance(expr.typ, (StringLyraType, ListLyraType)):
            return False
        elif isinstance(expr, Subscription):
            return False
        elif isinstance(expr, UnaryBooleanOperation):
            return self.check_if_interval_support(expr.expression)
        return True

    @property
    def input_var(self) -> VariableIdentifier:
        return VariableIdentifier(StringLyraType(), '.IN')

    @property
    def relationship_var(self) -> VariableIdentifier:
        return VariableIdentifier(StringLyraType(), '.REL')

    @property
    def relationship_state(self) -> IntervalState:
        return self.store[self.relationship_var]

    @property
    def relationships(self) -> dict:
        return self.relationship_state.store

    @property
    def stack_top(self) -> MultiInputAssumptionLattice:
        return self.store[self.input_var].lattice

    def interval_to_assmp_state(self, interval_state: IntervalState) -> 'AssumptionState':
        """Overwrites information of the current store with information from the interval state

        :param interval_state:
        :return:
        """
        for var, interval in interval_state.store.items():
            type_assumption = self.store[var].type_assumption
            self.store[var] = AssumptionLattice(type_assumption)
        return self

    class AssumptionRefinement(ExpressionVisitor):
        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr, assumption=None, state=None):
            #TODO
            #if isinstance(expr.key, Literal):
            #    self.assume_length_assmp(expr.target, expr.key, state)
            return state

        #def assume_length_assmp(self, target: VariableIdentifier, min_length, state):
        #    length_var = [v for v in state.variables if v.name == f"len_{target.name}"]
        #    assert len(length_var) == 1
        #    cond_type = BooleanLyraType()
        #    operator = BinaryComparisonOperation.Operator.GtE
        #    condition = BinaryComparisonOperation(cond_type, length_var[0], operator, min_length)
        #    state.assume([condition])

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
            state.new_input = AssumptionLattice(type_assmp).meet(assumption)
            if state.store[state.input_var].lattice.infoloss:
                if len(state.store[state.input_var].stack) == 1:
                    state.store[state.input_var].lattice.infoloss = False
            return state

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, assumption=None, state=None):
            return self.visit(expr.expression, AssumptionLattice(), state)

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, assumption=None, state=None):
            state.store[expr].type_assumption.meet(assumption.type_assumption)
            expr_type = TypeLattice.from_lyra_type(expr.typ)
            state.store[expr].type_assumption.meet(expr_type)
            return state

        #@copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        #def visit_LengthIdentifier(self, expr: LengthIdentifier, state=None, evaluation=None):
        #    return state #TODO

    _refinement = AssumptionRefinement()
