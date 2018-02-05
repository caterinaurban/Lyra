"""
Assumption Domain
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from copy import deepcopy
from typing import List

import math

from lyra.abstract_domains.numerical.interval_domain import IntervalState, IntervalLattice
from lyra.abstract_domains.quality.assumption_lattice import TypeLattice, AssumptionLattice, \
    InputAssumptionLattice, MultiInputAssumptionLattice

from lyra.abstract_domains.quality.simple_relation_lattice import SimpleRelationsLattice, \
    SimpleExpression, SimpleRelation
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import Expression, VariableIdentifier, ExpressionVisitor, \
    BinaryComparisonOperation, Range, BinaryOperation, UnaryOperation, LengthIdentifier, \
    Subscription, ListDisplay, Identifier, Literal
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
        :return: number of iterations as a tuple (start, end, step)
        """
        if isinstance(condition, BinaryComparisonOperation):
            if condition.operator == BinaryComparisonOperation.Operator.In:
                in_cond = condition.right
                if isinstance(in_cond, Range):
                    start = SimpleExpression.from_expression(in_cond.start)
                    end = SimpleExpression.from_expression(in_cond.end)
                    step = SimpleExpression.from_expression(in_cond.step)
                    if start is None or end is None or step is None:
                        return None
                    if step == SimpleExpression(const=1):
                        return end.sub(start)
                    elif start.is_constant() and end.is_constant() and step.is_constant():
                        value = math.ceil((end.const - start.const) / step.const)
                        return SimpleExpression(const=value)
                    else:
                        error = f"Iteration analysis of {condition} is not implemented."
                        raise NotImplementedError(error)
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
        self.store[self.relationship_var] = SimpleRelationsLattice()
        for var in [v for v in variables if v.typ == BooleanLyraType()]:
            self.store[var].range_assumption.meet(IntervalLattice(0, 1))
        self.new_input = None

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        error = 'AssumptionState for forward assign statement analysis is not supported!'
        raise NotImplementedError(error)

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'AssumptionState':
        self.stack_top.condition = condition
        range_info = self.assume_range_info(condition)
        self._refinement.visit(condition, AssumptionLattice(), self)
        if range_info is not None:
            self.apply_range_info_to_assmps(range_info)
        relation = SimpleRelation.from_expression(condition)
        if relation is not None:
            self.relationships.add(relation)
        return self

    def assume_range_info(self, condition: Expression):
        """Executes assume using the IntervalState.

        :param condition: the condition that is assumed
        :return: the interval Store after executing assume or None if not executable in the
        IntervalState
        """
        interval_state = self.create_interval_state([condition])
        if interval_state is None:
            return None
        interval_state.assume({condition})
        return interval_state.store

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
            left_assumption = deepcopy(self.store[left])
            interval_store = self.substitute_range_info(left, right)
            self.store[left].top()
            self._refinement.visit(right, left_assumption, self)
            if interval_store is not None:
                self.apply_range_info_to_assmps(interval_store)
            if self.new_input is not None:
                input_id = VariableIdentifier(IntegerLyraType(), f".ID={self.pp.line}")
                relations = self.relationships.remove_relations_for_input(left, input_id)
                assmp = self.new_input[0]
                delimiter = self.new_input[1]
                input_assmp = InputAssumptionLattice(self.pp.line, assmp, relations)
                if delimiter is not None:
                    len_var = LengthIdentifier(left)
                    len_assmp = self.store[len_var].range_assumption.lower
                    iters = SimpleExpression(const=max(0, len_assmp))
                    assmps = [input_assmp]
                    input_assmp = MultiInputAssumptionLattice(iters, assmps, self.pp, delimiter)
                self.stack_top.add_assumption_front(input_assmp)
                self.substitute_relationships_in_input(left, input_id)
            else:
                self.relationships.substitute_all(left, right)
                self.substitute_relationships_in_input(left, right)
                if isinstance(right, ListDisplay):
                    list_id = LengthIdentifier(left)
                    list_len = Literal(IntegerLyraType(), str(len(right.items)))
                    self.relationships.substitute_all(list_id, list_len)
                    self.substitute_relationships_in_input(list_id, list_len)
            self.new_input = None
            return self
        if isinstance(left, Subscription):
            self._refinement.visit(left, self.store[left.target], self)
            self._refinement.visit(right, self.store[left.target], self)
            return self
        error = f'Substitution for {left} not yet implemented!'
        raise NotImplementedError(error)

    def apply_range_info_to_assmps(self, ranges: dict):
        """Applies information from a dictionary variable -> IntervalLattice to the assumptions.

        :param ranges: map from variables to intervals
        """
        for var_expr, range_val in ranges.items():
            self.store[var_expr].range_assumption.bottom().join(range_val)

    def substitute_range_info(self, left: Expression, right: Expression):
        """Uses an IntervalState to get information about the range of values.
        Substitute in IntervalState will only be executed if the types are valid for an interval
        analysis.

        :param left: expression of the left hand side of the substitution
        :param right: expression of the right hand side of the substitution
        :return: Map from variables to intervals or None if interval analysis cannot be done
        """
        interval_state = self.create_interval_state([left, right])
        if interval_state is None:
            return None
        interval_state.substitute({left}, {right})
        return interval_state.store

    def create_interval_state(self, exprs: [Expression]):
        """Creates an interval state using the variables in the expression. Returns None if one of
        the variables cannot be used for interval analysis.

        :param exprs: variables in this expression are used to create an IntervalState
        :return: newly created IntervalState with variables used in the exprs argument
        """
        interval_store = self.create_interval_store(exprs, {})
        if interval_store is None:
            return None
        variables = [v for v in interval_store]
        interval_state = IntervalState(variables)
        for var, interval in interval_store.items():
            interval_state.store[var] = interval
            if isinstance(var.typ, BooleanLyraType):
                interval_state.store[var].meet(IntervalLattice(0, 1))
        return interval_state

    def create_interval_store(self, exprs: [Expression], store: dict):
        """Creates an interval store using the variables in the expression. Returns None if one of
        the variables cannot be used for interval analysis.

        :param exprs: variables in this expression are used to create an interval store
        :param store: map from variables to IntervalLattice objects
        :return: newly created map from variables to IntervalLattice objects with variables
        used in the exprs argument
        """
        interval_ok = True
        for expr in exprs:
            if isinstance(expr, VariableIdentifier):
                if not isinstance(expr.typ, (IntegerLyraType, FloatLyraType, BooleanLyraType)):
                    return None
                if expr not in store:
                    store[expr] = deepcopy(self.store[expr].range_assumption)
            elif isinstance(expr, UnaryOperation):
                interval_ok = self.create_interval_store([expr.expression], store)
            elif isinstance(expr, BinaryOperation):
                interval_ok = self.create_interval_store([expr.left, expr.right], store)
            elif isinstance(expr, Range):
                interval_ok = self.create_interval_store([expr.start, expr.end, expr.step], store)
            elif isinstance(expr, (Subscription, LengthIdentifier)):
                return None
        if not interval_ok:
            return None
        return store

    def substitute_relationships_in_input(self, var: Identifier, right):
        """Substitutes a variable if it appears in a relationship in the input collection.

        :param var: variable that is substituted
        :param right: expression the variable is substituted with
        """
        for assmps in self.input_assmp_stack:
            self.substitute_relation_in_assmp(var, right, assmps)

    def substitute_relation_in_assmp(self, var: Identifier, right, assmp):
        """Substitutes a variable for an expression in the given assumption.

        :param var: variable that is substituted
        :param right: expression the variable is substituted with
        :param assmp: assumption whose relation variables have to be substituted
        """

        if isinstance(assmp, MultiInputAssumptionLattice):
            if assmp.iterations.var == var:
                right_expr = SimpleExpression.from_expression(right)
                if right_expr is None:
                    if assmp.iterations.var == var:
                        self.stack_top.assmps.clear()
                        self.stack_top.infoloss = True
                        return
                assmp.iterations.substitute_expr(var, right_expr)
            for a in assmp.assmps:
                self.substitute_relation_in_assmp(var, right, a)
        else:
            assmp.relations.substitute_all(var, right)

    @property
    def input_var(self) -> VariableIdentifier:
        return VariableIdentifier(StringLyraType(), '.IN')

    @property
    def relationship_var(self) -> VariableIdentifier:
        return VariableIdentifier(StringLyraType(), '.REL')

    @property
    def relationships(self) -> SimpleRelationsLattice:
        return self.store[self.relationship_var]

    @property
    def input_assmp_stack(self) -> [MultiInputAssumptionLattice]:
        return self.store[self.input_var].stack

    @property
    def stack_top(self) -> MultiInputAssumptionLattice:
        return self.store[self.input_var].lattice

    class AssumptionRefinement(ExpressionVisitor):
        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr, assumption=None, state=None):
            key = expr.key
            target = expr.target
            if isinstance(target, VariableIdentifier):
                length_target = LengthIdentifier(target)
                if isinstance(key, VariableIdentifier):
                    length_relation = SimpleRelation(True, key, 1, False, length_target)
                    state.relationships.add(length_relation)
                elif isinstance(key, Literal):
                    length_min = int(key.val) + 1
                    assmp = AssumptionLattice(TypeLattice().integer(), IntervalLattice(length_min))
                    state.store[length_target].meet(assmp.meet(assumption))
            return state

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
            state.new_input = (AssumptionLattice(type_assmp).meet(assumption), None)
            if state.stack_top.infoloss:
                if len(state.store[state.input_var].stack) == 1:
                    state.stack_top.infoloss = False
            return state

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Split)
        def visit_Split(self, expr, assumption=None, state=None):
            self.visit(expr.target, assumption, state)
            if expr.delimiter is None:
                state.new_input = (state.new_input[0], "")
            else:
                state.new_input = (state.new_input[0], expr.delimiter)
            return state  # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, assumption=None, state=None):
            return self.visit(expr.expression, AssumptionLattice(), state)

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, assumption=None, state=None):
            state.store[expr].meet(assumption)
            expr_type = TypeLattice.from_lyra_type(expr.typ)
            state.store[expr].type_assumption.meet(expr_type)
            return state

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr, assumption=None, state=None):
            return state

    _refinement = AssumptionRefinement()
