"""
Abstract Domain
===============

Interface of an abstract domain.
Abstract domain elements support lattice operations and program statements.

:Author: Caterina Urban
"""


from abc import ABCMeta, abstractmethod
from collections import defaultdict
from copy import deepcopy
from typing import Set, Optional, List, Type, Dict, Any, Union

from lyra.abstract_domains.lattice import Lattice
from lyra.core.expressions import Expression, VariableIdentifier, Subscription, Slicing, AttributeReference, Literal, \
    NegationFreeExpression, UnaryBooleanOperation, BinaryBooleanOperation, \
    BinaryComparisonOperation
from lyra.core.statements import ProgramPoint
from lyra.core.types import BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType, \
    ContainerLyraType, DictLyraType
from lyra.core.utils import copy_docstring


class State(Lattice, metaclass=ABCMeta):
    """Analysis state. A mutable element of an abstract domain.

    .. warning::
        Lattice operations and statements modify the current state.
    """

    def __init__(self, precursory: 'State' = None):
        super().__init__()
        self._result = set()
        self._pp = None
        self._precursory = precursory

    @property
    def result(self):
        """Result of the previously analyzed statement."""
        return self._result

    @result.setter
    def result(self, result: Set[Expression]):
        self._result = result

    @property
    def pp(self):
        """Program point of the currently analyzed statement."""
        return self._pp

    @pp.setter
    def pp(self, pp: ProgramPoint):
        self._pp = pp

    @property
    def precursory(self):
        """Current precursory analysis state."""
        return self._precursory

    @precursory.setter
    def precursory(self, precursory: 'State'):
        self._precursory = precursory

    def __repr__(self):
        return ", ".join("{}".format(expression) for expression in self.result)

    @abstractmethod
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'State':
        """Assign an expression to a variable identifier

        :param left: the variable identifier to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """

    @abstractmethod
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'State':
        """Assign an expression to a subscription

        :param left: the subscription to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """

    @abstractmethod
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'State':
        """Assign an expression to a slicing

        :param left: the slicing to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """

    def _assign(self, left: Expression, right: Expression) -> 'State':
        """Assign an expression to another expression.

        .. warning::
            The current state could also be top.

        :param left: expression to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment

        """
        if isinstance(left, VariableIdentifier):
            return self._assign_variable(left, right)
        elif isinstance(left, AttributeReference):
            raise NotImplementedError(f"Assignment to attribute reference {left} is unsupported!")
        elif isinstance(left, Subscription):
            return self._assign_subscription(left, right)
        elif isinstance(left, Slicing):
            return self._assign_slicing(left, right)
        raise ValueError(f"Unexpected assignment to {left}!")

    def assign(self, left: Set[Expression], right: Set[Expression]) -> 'State':
        """Assign an expression to another expression.

        :param left: set of expressions representing the expression to be assigned to
        :param right: set of expressions representing the expression to assign
        :return: current state modified by the assignment

        """
        if self.is_bottom():
            return self
        self.big_join([deepcopy(self)._assign(lhs, rhs) for lhs in left for rhs in right])
        self.result = set()  # assignments have no result, only side-effects
        return self

    def _assume_literal(self, condition: Literal, neg: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: literal representing the assumed condition
        :param neg: whether the assumption should be negated (default: False)
        :return: current state modified to satisfy the assumption

        """
        if isinstance(condition.typ, BooleanLyraType):
            if (condition.val == 'True') ^ neg:
                return self
            assert condition.val == 'False'
            return self.bottom()
        elif isinstance(condition.typ, (IntegerLyraType, FloatLyraType)):
            if (float(condition.val) != 0) ^ neg:
                return self
            assert float(condition.val) == 0
            return self.bottom()
        assert isinstance(condition.typ, StringLyraType)
        if condition.val ^ neg:
            return self
        return self.bottom()

    @abstractmethod
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: variable representing the assumed condition
        :param neg: whether the assumption should be negated (default: False)
        :return: current state modified to satisfy the assumption

        """

    def _assume_unary_boolean(self, condition: UnaryBooleanOperation) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: unary boolean operation representing the assumed condition
        :return: current state modified to satisfy the assumption

        """
        if isinstance(condition.expression, Literal):
            return self._assume_literal(condition.expression, neg=True)
        assert isinstance(condition.expression, VariableIdentifier)
        return self._assume_variable(condition.expression, neg=True)

    def _assume_binary_boolean(self, condition: BinaryBooleanOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: binary boolean operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """
        if condition.operator == BinaryBooleanOperation.Operator.And:
            right = deepcopy(self)._assume(condition.right, bwd=bwd)
            return self._assume(condition.left, bwd=bwd).meet(right)
        assert condition.operator == BinaryBooleanOperation.Operator.Or
        right = deepcopy(self)._assume(condition.right, bwd=bwd)
        return self._assume(condition.left, bwd=bwd).join(right)

    @abstractmethod
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: equal comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: not equal comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: less than comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: less than or equal comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: greater comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: greater than or equal comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: is comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: is not comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: in comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    @abstractmethod
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: not in comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """

    def _assume_binary_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: binary comparison operation representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """
        if condition.operator == BinaryComparisonOperation.Operator.Eq:
            return self._assume_eq_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.NotEq:
            return self._assume_noteq_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.Lt:
            return self._assume_lt_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.LtE:
            return self._assume_lte_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.Gt:
            return self._assume_gt_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.GtE:
            return self._assume_gte_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.Is:
            return self._assume_is_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.IsNot:
            return self._assume_isnot_comparison(condition, bwd=bwd)
        elif condition.operator == BinaryComparisonOperation.Operator.In:
            return self._assume_in_comparison(condition, bwd=bwd)
        assert condition.operator == BinaryComparisonOperation.Operator.NotIn
        return self._assume_notin_comparison(condition, bwd=bwd)

    def _assume(self, condition: Expression, bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        .. warning::
            The current state could also be top.

        :param condition: expression representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """
        normal = self._negation_free.visit(condition)
        if isinstance(normal, Literal):
            return self._assume_literal(normal)
        elif isinstance(normal, VariableIdentifier):
            return self._assume_variable(normal)
        elif isinstance(normal, UnaryBooleanOperation):
            return self._assume_unary_boolean(normal)
        elif isinstance(normal, BinaryBooleanOperation):
            return self._assume_binary_boolean(normal, bwd=bwd)
        elif isinstance(normal, BinaryComparisonOperation):
            return self._assume_binary_comparison(normal, bwd=bwd)
        raise ValueError(f"Assumption of a {normal.__class__.__name__} expression is unsupported!")

    def assume(self, condition: Set[Expression], bwd: bool = False) -> 'State':
        """Assume that some condition holds in the current state.

        :param condition: set of expressions representing the assumed condition
        :param bwd: whether the assumption happens in a backward analysis (default: False)
        :return: current state modified to satisfy the assumption

        """
        if self.is_bottom():
            return self
        self.big_join([deepcopy(self)._assume(expr, bwd=bwd) for expr in condition])
        return self

    def before(self, pp: ProgramPoint, precursory: Optional['State']) -> 'State':
        """Set the program point of the currently analyzed statement
        and the current precursory analysis state.

        :param pp: current program point
        :param precursory: current precursory analysis state
        :return: current state modified to set the current program point and precursory state
        """
        self.pp = pp
        self.precursory = precursory
        return self

    @abstractmethod
    def enter_if(self) -> 'State':
        """Enter a conditional if statement.

        .. warning::
            The current state could also be bottom or top.

        :return: current state modified to enter a conditional if statement

        """

    @abstractmethod
    def exit_if(self) -> 'State':
        """Exit a conditional if statement.

        .. warning::
            The current state could also be bottom or top.

        :return: current state modified to enter a conditional if statement

        """

    @abstractmethod
    def enter_loop(self) -> 'State':
        """Enter a loop.

        .. warning::
            The current state could also be bottom or top.

        :return: current state modified to enter a loop

        """

    @abstractmethod
    def exit_loop(self) -> 'State':
        """Exit a loop.

        .. warning::
            The current state could also be bottom or top.

        :return: current state modified to exit a loop

        """

    def filter(self, bwd: bool = False) -> 'State':
        """Assume that the current result holds in the current state.

        :param bwd: whether the filtering happens in a backward analysis (default: False)
        :return: current state modified to satisfy the current result

        """
        self.assume(self.result, bwd=bwd)
        self.result = set()  # filtering has no result, only side-effects
        return self

    @abstractmethod
    def forget_variable(self, variable: VariableIdentifier) -> 'State':
        """Forget a variable value.

        :param variable: variable whose value is to be forgotten
        :return: current state modified to have forgotten the given variable value
        """

    @abstractmethod
    def _output(self, output: Expression) -> 'State':
        """Outputs something in the current state.

        .. warning::
            The current state could also be top.

        :param output: expression representing the output
        :return: current state modified by the output

        """

    def output(self, output: Set[Expression]) -> 'State':
        """Outputs something in the current state.

        :param output: set of expressions representing the output
        :return: current state modified by the output

        """
        if self.is_bottom():
            return self
        self.big_join([deepcopy(self)._output(expr) for expr in output])
        self.result = set()  # outputs have no result, only side-effects
        return self

    def raise_error(self) -> 'State':
        """Raise an error.

        :return: current state modified to be the bottom state
        """
        return self.bottom()

    @abstractmethod
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'State':
        """substitute an expression to a variable identifier

        :param left: the variable identifier to be substituted to
        :param right: expression to substitute
        :return: current state modified by the substitution
        """

    @abstractmethod
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'State':
        """substitute an expression to a subscription

        :param left: the subscription to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution
        """

    @abstractmethod
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'State':
        """substitute an expression to a slicing

        :param left: the slicing to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution
        """

    def _substitute(self, left: Expression, right: Expression) -> 'State':
        """Substitute an expression to another expression.

        .. warning::
            The current state could also be top.

        :param left: expression to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution

        """
        if isinstance(left, VariableIdentifier):
            return self._substitute_variable(left, right)
        elif isinstance(left, AttributeReference):
            raise NotImplementedError(f"Substitution of attribute reference {left} is unsupported!")
        elif isinstance(left, Subscription):
            return self._substitute_subscription(left, right)
        elif isinstance(left, Slicing):
            return self._substitute_slicing(left, right)
        raise ValueError(f"Unexpected substitution of {left}!")

    def substitute(self, left: Set[Expression], right: Set[Expression]) -> 'State':
        """Substitute an expression to another expression.

        :param left: set of expressions representing the expression to be substituted
        :param right: set of expressions representing the expression to substitute
        :return: current state modified by the substitution

        """
        if self.is_bottom():
            return self
        self.big_join([deepcopy(self)._substitute(l, r) for l in left for r in right])
        self.result = set()  # assignments have no result, only side-effects
        return self

    _negation_free = NegationFreeExpression()


class StateWithSummarization(State, metaclass=ABCMeta):

    def _assign_summary(self, left: Union[Subscription, Slicing], right: Expression) -> 'StateWithSummarization':
        """Assign an expression to a summary variable.

        :param left: summary variable to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """
        # copy the current state
        current: StateWithSummarization = deepcopy(self)
        # perform the substitution on the copy of the current state
        target = left
        while isinstance(target, (Subscription, Slicing)):    # recurse to VariableIdentifier target
            target = target.target
        self._assign_variable(target, right)
        # perform a weak update on the current state
        return self.join(current)

    @abstractmethod
    def _assign_dictionary_subscription(self, left: Subscription, right: Expression) -> 'StateWithSummarization':
        """Assign an expression to a dictionary subscription

        :param left: the dictionary subscription to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'StateWithSummarization':
        if isinstance(left.target.typ, DictLyraType):
            return self._assign_dictionary_subscription(left, right)
        return self._assign_summary(left, right)

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'StateWithSummarization':
        return self._assign_summary(left, right)

    @abstractmethod
    def _weak_update(self, variables: Set[VariableIdentifier], previous: 'StateWithSummarization'):
        """Weaken a strong update.

        :param variables: variables involved in the weak update
        :param previous: state before the strong update
        :return: current state modified to have undergone a weak update (instead of a strong one)
        """

    @copy_docstring(State._assume_binary_comparison)
    def _assume_binary_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # identify involved container identifiers
        containers: Set[VariableIdentifier] = {var for var in condition.ids() if isinstance(var.typ, ContainerLyraType)}
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
        if containers:
            return self._weak_update(containers, current)
        return self

    def _substitute_summary(self, left: Union[Subscription, Slicing], right: Expression) -> 'StateWithSummarization':
        """Substitute an expression to a summary variable.

        :param left: summary variable to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution
        """
        # copy the current state
        current: StateWithSummarization = deepcopy(self)
        # perform the substitution on the copy of the current state
        target = left
        while isinstance(target, (Subscription, Slicing)):    # recurse to VariableIdentifier target
            target = target.target
        self._substitute_variable(target, right)
        # check for errors turning the state into bottom
        if self.is_bottom():
            return self
        # if there are not errors, perform a weak update on the current state
        return self.join(current)

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'StateWithSummarization':
        return self._substitute_summary(left, right)

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'StateWithSummarization':
        return self._substitute_summary(left, right)


class ProductState(State):
    """Product analysis state. A mutable element of a product abstract domain.
    (MRO: ProductState, State, Lattice)
    
    .. warning::
        Lattice operations and statements modify the current state.
    """

    def __init__(self, states: List[Type[State]], arguments=None, precursory: State = None):
        super().__init__(precursory)
        if arguments is None:
            arguments: Dict[Type, Dict[str, Any]] = defaultdict(lambda: dict())
        self._states = [deepcopy(state(**arguments[state])) for state in states]

    @property
    def states(self):
        """Current list of states."""
        return self._states
    
    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return "\n".join(str(state) for state in self.states)

    @copy_docstring(State.bottom)
    def bottom(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.bottom()
        return self

    @copy_docstring(State.top)
    def top(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.top()
        return self

    @copy_docstring(State.is_bottom)
    def is_bottom(self) -> bool:
        return any(state.is_bottom() for state in self.states)

    @copy_docstring(State.is_top)
    def is_top(self) -> bool:
        return all(state.is_top() for state in self.states)

    @copy_docstring(State._less_equal)
    def _less_equal(self, other: 'ProductState') -> bool:
        return all(state.less_equal(other.states[i]) for i, state in enumerate(self.states))

    @copy_docstring(State._join)
    def _join(self, other: 'ProductState') -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.join(other.states[i])
        return self

    @copy_docstring(State._meet)
    def _meet(self, other: 'ProductState'):
        for i, state in enumerate(self.states):
            self.states[i] = state.meet(other.states[i])
        return self

    @copy_docstring(State._widening)
    def _widening(self, other: 'ProductState'):
        for i, state in enumerate(self.states):
            self.states[i] = state.widening(other.states[i])
        return self

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assign_variable(left, right)
        return self

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assign_subscription(left, right)
        return self

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assign_slicing(left, right)
        return self

    @copy_docstring(State._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_variable(condition, neg=neg)
        return self

    @copy_docstring(State._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_eq_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_noteq_comparison)
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_noteq_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_lt_comparison)
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_lt_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_lte_comparison)
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_lte_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_gt_comparison)
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_gt_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_gte_comparison)
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_gte_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_is_comparison)
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_is_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_isnot_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_in_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._assume_notin_comparison(condition, bwd=bwd)
        return self

    @copy_docstring(State.before)
    def before(self, pp: ProgramPoint, precursory: Optional['State']) -> 'ProductState':
        super().before(pp, precursory)
        for i, state in enumerate(self.states):
            self.states[i] = state.before(pp, precursory)
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.enter_if()
        return self

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.exit_if()
        return self

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.enter_loop()
        return self

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.exit_loop()
        return self

    @copy_docstring(State.forget_variable)
    def forget_variable(self, variable: VariableIdentifier) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.forget_variable(variable)
        return self

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state.output({output})
        return self

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._substitute_variable(left, right)
        return self

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._substitute_subscription(left, right)
        return self

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'ProductState':
        for i, state in enumerate(self.states):
            self.states[i] = state._substitute_slicing(left, right)
        return self
