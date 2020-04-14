"""
APRON-based Abstract Domain
===========================

Abstract domain based on APRON to be used for **numerical analysis**.
The set of possible numerical values of a program variable in a program state
is represented by a conjunction of (more of less complex) linear constraints.

:Authors: Caterina Urban
"""
from abc import ABCMeta
from copy import deepcopy
from typing import Set, Type, Union

from apronpy.abstract1 import PyAbstract1
from apronpy.coeff import PyMPQIntervalCoeff
from apronpy.environment import PyEnvironment
from apronpy.interval import PyMPQInterval
from apronpy.lincons1 import PyLincons1Array
from apronpy.linexpr1 import PyLinexpr1
from apronpy.manager import PyManager
from apronpy.tcons1 import PyTcons1Array, PyTcons1
from apronpy.texpr1 import PyTexpr1
from apronpy.var import PyVar

from lyra.abstract_domains.state import State, StateWithSummarization
from lyra.core.expressions import VariableIdentifier, Expression, \
    BinaryComparisonOperation, NegationFreeExpression, Lyra2APRON, Slicing, Subscription, LengthIdentifier, \
    ListDisplay, TupleDisplay, SetDisplay, DictDisplay
from lyra.core.utils import copy_docstring


class Lyra2APRONWithSummarization(Lyra2APRON):

    @copy_docstring(Lyra2APRON.visit_LengthIdentifier)
    def visit_LengthIdentifier(self, expr: 'LengthIdentifier', environment=None, usub=False):
        assert not usub
        return PyTexpr1.cst(environment, PyMPQIntervalCoeff(PyMPQInterval.top()))

    @copy_docstring(Lyra2APRON.visit_ListDisplay)
    def visit_ListDisplay(self, expr: 'ListDisplay', environment=None, usub=False) -> Set[PyTexpr1]:
        assert not usub
        texpr1s = set()
        for item in expr.items:
            visited = self.visit(item, environment)
            assert isinstance(visited, PyTexpr1)    # TODO: relax this assumtion
            texpr1s.add(visited)
        return texpr1s

    @copy_docstring(Lyra2APRON.visit_TupleDisplay)
    def visit_TupleDisplay(self, expr: 'TupleDisplay', environment=None, usub=False) -> Set[PyTexpr1]:
        assert not usub
        texpr1s = set()
        for item in expr.items:
            visited = self.visit(item, environment)
            assert isinstance(visited, PyTexpr1)    # TODO: relax this assumtion
            texpr1s.add(visited)
        return texpr1s

    @copy_docstring(Lyra2APRON.visit_SetDisplay)
    def visit_SetDisplay(self, expr: 'SetDisplay', environment=None, usub=False) -> Set[PyTexpr1]:
        assert not usub
        texpr1s = set()
        for item in expr.items:
            visited = self.visit(item, environment)
            assert isinstance(visited, PyTexpr1)    # TODO: relax this assumtion
            texpr1s.add(visited)
        return texpr1s

    @copy_docstring(Lyra2APRON.visit_DictDisplay)
    def visit_DictDisplay(self, expr: 'DictDisplay', environment=None, usub=False):
        assert not usub
        texpr1s = set()
        for item in expr.keys:
            visited = self.visit(item, environment)
            assert isinstance(visited, PyTexpr1)    # TODO: relax this assumtion
            texpr1s.add(visited)
        for item in expr.values:
            visited = self.visit(item, environment)
            assert isinstance(visited, PyTexpr1)    # TODO: relax this assumtion
            texpr1s.add(visited)
        return texpr1s

    @copy_docstring(Lyra2APRON.visit_Subscription)
    def visit_Subscription(self, expr: 'Subscription', environment=None, usub=False):
        assert not usub
        return PyTexpr1.var(environment, PyVar(expr.target.name))

    @copy_docstring(Lyra2APRON.visit_Slicing)
    def visit_Slicing(self, expr: 'Slicing', environment=None, usub=False):
        assert not usub
        return PyTexpr1.var(environment, PyVar(expr.target.name))


class APRONStateWithSummarization(StateWithSummarization, metaclass=ABCMeta):
    """Analysis state based on APRON. An element of the abstract domain.

    Conjunction of constraints constraining the value of each variable.
    The value of all program variables is unconstrained by default.

    .. note:: Program variables storing collections are abstracted via summarization.

    .. document private methods
    .. automethod:: APRONState._assign
    .. automethod:: APRONState._assume
    .. automethod:: APRONState._output
    .. automethod:: APRONState._substitute

    """

    def __init__(self, domain: Type[PyAbstract1],
                 variables: Set[VariableIdentifier], precursory: State = None):
        super().__init__(precursory=precursory)
        self.domain = domain
        _variables = list()
        for variable in variables:
            _variables.append(PyVar(variable.name))
        self.environment = PyEnvironment([], _variables)
        self.state = self.domain(self.manager, self.environment)

    @copy_docstring(State.bottom)
    def bottom(self):
        self.state = self.domain.bottom(self.manager, self.environment)
        return self

    @copy_docstring(State.top)
    def top(self):
        self.state = self.domain.top(self.manager, self.environment)
        return self

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return '{}'.format(self.state)

    @copy_docstring(State.is_bottom)
    def is_bottom(self) -> bool:
        return self.state.is_bottom()

    @copy_docstring(State.is_top)
    def is_top(self) -> bool:
        return self.state.is_top()

    def bound_variable(self, variable: PyVar):
        return self.state.bound_variable(variable)

    def bound_linexpr(self, linexpr: PyLinexpr1):
        return self.state.bound_linexpr(linexpr)

    def bound_texpr(self, texpr: PyTexpr1):
        return self.state.bound_texpr(texpr)

    @copy_docstring(State._less_equal)
    def _less_equal(self, other: 'APRONStateWithSummarization') -> bool:
        return self.state <= other.state

    @copy_docstring(State._join)
    def _join(self, other: 'APRONStateWithSummarization') -> 'APRONStateWithSummarization':
        self.state = self.state.join(other.state)
        return self

    @copy_docstring(State._meet)
    def _meet(self, other: 'APRONStateWithSummarization') -> 'APRONStateWithSummarization':
        self.state = self.state.meet(other.state)
        return self

    @copy_docstring(State._widening)
    def _widening(self, other: 'APRONStateWithSummarization') -> 'APRONStateWithSummarization':
        self.state = self.state.widening(other.state)
        return self

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'APRONStateWithSummarization':
        expr = self._lyra2apron.visit(right, self.environment)
        if isinstance(expr, PyTexpr1):
            self.state = self.state.assign(PyVar(left.name), expr)
        else:
            assert isinstance(expr, Set)
            state = deepcopy(self.state).bottom(self.manager, self.environment)
            for item in expr:
                state = state.join(deepcopy(self.state).assign(PyVar(left.name), item))
            self.state = state
        return self

    def _assign_summary(self, left: Union[Subscription, Slicing], right: Expression):
        """Assign an expression to a summary variable.

        :param left: summary variable to be assigned to
        :param right: expression to assign
        :return: current state modified by the assignment
        """
        # copy the current state
        current: APRONStateWithSummarization = deepcopy(self)
        # perform the substitution on the copy of the current state
        target = left
        while isinstance(target, (Subscription, Slicing)):  # recurse to VariableIdentifier target
            target = target.target
        self._assign_variable(target, right)
        # perform a weak update on the current state
        return self.join(current)

    @copy_docstring(State._assign_subscription)
    def _assign_subscription(self, left: Subscription, right: Expression):
        return self._assign_summary(left, right)    # TODO: implement correctly

    @copy_docstring(State._assign_slicing)
    def _assign_slicing(self, left: Slicing, right: Expression):
        return self._assign_summary(left, right)    # TODO: implement correctly

    @copy_docstring(State._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'APRONStateWithSummarization':
        raise NotImplementedError(f"Assumption of {condition.__class__.__name__} is unsupported!")

    @copy_docstring(StateWithSummarization._weak_update)
    def _weak_update(self, variables: Set[VariableIdentifier], previous: 'APRONStateWithSummarization'):
        given_names = {var.name for var in variables}
        # find constraints involving the given variables
        current_array: PyLincons1Array = self.state.to_lincons
        current_unstable = list()
        for i in range(len(current_array)):
            lincons1 = current_array.get(i)
            for name in given_names:
                if str(lincons1.get_coeff(PyVar(name))) != '0':
                    current_unstable.append(i)
                    break
        previous_array: PyLincons1Array = previous.state.to_lincons
        previous_unstable = list()
        for i in range(len(previous_array)):
            lincons1 = previous_array.get(i)
            for name in given_names:
                if str(lincons1.get_coeff(PyVar(name))) != '0':
                    previous_unstable.append(i)
                    break
        # join the constraints involving the given variables
        all_names = set()
        for i in range(len(self.environment)):
            all_names.add(self.environment.environment.contents.var_of_dim[i].decode('utf-8'))
        other_names = all_names - given_names

        current_lincons1s = list()
        for i in current_unstable:
            current_lincons1s.append(current_array.get(i))
        current_given = deepcopy(self.state).forget([PyVar(name) for name in other_names])
        current_given_array = current_given.to_lincons
        for i in range(len(current_given_array)):
            current_lincons1s.append(current_given_array.get(i))
        current_array1 = PyLincons1Array(current_lincons1s, self.environment)
        current_abstract1 = self.domain(self.manager, self.environment, array=current_array1)

        previous_lincons1s = list()
        for i in previous_unstable:
            previous_lincons1s.append(previous_array.get(i))
        previous_given = deepcopy(previous.state).forget([PyVar(name) for name in other_names])
        previous_given_array = previous_given.to_lincons
        for i in range(len(previous_given_array)):
            previous_lincons1s.append(previous_given_array.get(i))
        previous_array1 = PyLincons1Array(previous_lincons1s, self.environment)
        previous_abstract1 = self.domain(self.manager, self.environment, array=previous_array1)

        joined_abstract1 = current_abstract1.join(previous_abstract1)
        joined_array = joined_abstract1.to_lincons
        # add the stable constraints to the result
        lincons1s = list()
        for i in range(len(joined_array)):
            lincons1s.append(joined_array.get(i))
        stable = deepcopy(self.state).forget([PyVar(name) for name in given_names])
        stable_array = stable.to_lincons
        for i in range(len(stable_array)):
            lincons1s.append(stable_array.get(i))
        abstract1 = self.domain(self.manager, self.environment, array=PyLincons1Array(lincons1s, self.environment))
        self.state = abstract1
        return self
    
    def _assume_any_comparison(self, condition: BinaryComparisonOperation):
        cond = self._lyra2apron.visit(condition, self.environment)
        if isinstance(cond, PyTcons1):
            array = PyTcons1Array([cond])
            self.state = self.state.meet(array)
        else:
            assert isinstance(cond, Set)
            state = deepcopy(self.state).bottom(self.manager, self.environment)
            for item in cond:
                array = PyTcons1Array([item])
                state = state.join(deepcopy(self.state).meet(array))
            self.state = state
        return self
    
    @copy_docstring(State._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_noteq_comparison)
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_lt_comparison)
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_lte_comparison)
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_gt_comparison)
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_gte_comparison)
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_is_comparison)
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        return self._assume_any_comparison(condition)

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'APRONStateWithSummarization':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'APRONStateWithSummarization':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'APRONStateWithSummarization':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'APRONStateWithSummarization':
        return self  # nothing to be done

    @copy_docstring(State.forget_variable)
    def forget_variable(self, variable: VariableIdentifier) -> 'APRONStateWithSummarization':
        self.state = self.state.forget([PyVar(variable.name)])
        return self

    @copy_docstring(State.output)
    def _output(self, output: Expression) -> 'APRONStateWithSummarization':
        return self  # nothing to be done

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'APRONStateWithSummarization':
        expr = self._lyra2apron.visit(right, self.environment)
        if isinstance(expr, PyTexpr1):
            self.state = self.state.substitute(PyVar(left.name), expr)
        else:
            assert isinstance(expr, Set)
            state = deepcopy(self.state).bottom(self.manager, self.environment)
            for item in expr:
                state = state.join(deepcopy(self.state).substitute(PyVar(left.name), item))
            self.state = state
        return self

    def _substitute_summary(self, left: Union[Subscription, Slicing], right: Expression):
        """Substitute an expression to a summary variable.

        :param left: summary variable to be substituted
        :param right: expression to substitute
        :return: current state modified by the substitution
        """
        # copy the current state
        current: APRONStateWithSummarization = deepcopy(self)
        # perform the substitution on the copy of the current state
        target = left
        while isinstance(target, (Subscription, Slicing)):  # recurse to VariableIdentifier target
            target = target.target
        self._substitute_variable(target, right)
        # check for errors turning the state into bottom
        if self.is_bottom():
            return self
        # if there are not errors, perform a weak update on the current state
        return self.join(current)

    @copy_docstring(State._substitute_subscription)
    def _substitute_subscription(self, left: Subscription, right: Expression):
        return self._substitute_summary(left, right)    # TODO: implement correctly

    @copy_docstring(State._substitute_slicing)
    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'StateWithSummarization':
        return self._substitute_summary(left, right)    # TODO: implement correctly

    _negation_free = NegationFreeExpression()
    _lyra2apron = Lyra2APRONWithSummarization()
    manager: PyManager
