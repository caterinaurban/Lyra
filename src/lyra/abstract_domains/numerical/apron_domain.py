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
from apronpy.linexpr1 import PyLinexpr1
from apronpy.manager import PyManager
from apronpy.tcons1 import PyTcons1Array, PyTcons1
from apronpy.texpr1 import PyTexpr1
from apronpy.var import PyVar

from lyra.abstract_domains.state import State, StateWithSummarization
from lyra.core.expressions import VariableIdentifier, Expression, BinaryBooleanOperation, \
    BinaryComparisonOperation, NegationFreeExpression, Lyra2APRON, Slicing, Subscription, LengthIdentifier, ListDisplay, \
    TupleDisplay
from lyra.core.utils import copy_docstring


class Lyra2APRONWithSummarization(Lyra2APRON):

    @copy_docstring(Lyra2APRON.visit_LengthIdentifier)
    def visit_LengthIdentifier(self, expr: 'LengthIdentifier', environment=None, usub=False):
        assert not usub
        return PyTexpr1.cst(environment, PyMPQIntervalCoeff(PyMPQInterval.top()))

    @copy_docstring(Lyra2APRON.visit_ListDisplay)
    def visit_ListDisplay(self, expr: 'ListDisplay', environment=None, usub=False):
        assert not usub
        return PyTexpr1.cst(environment, PyMPQIntervalCoeff(PyMPQInterval.top()))

    @copy_docstring(Lyra2APRON.visit_TupleDisplay)
    def visit_TupleDisplay(self, expr: 'TupleDisplay', environment=None, usub=False):
        assert not usub
        return PyTexpr1.cst(environment, PyMPQIntervalCoeff(PyMPQInterval.top()))

    @copy_docstring(Lyra2APRON.visit_SetDisplay)
    def visit_SetDisplay(self, expr: 'SetDisplay', environment=None, usub=False):
        assert not usub
        return PyTexpr1.cst(environment, PyMPQIntervalCoeff(PyMPQInterval.top()))

    @copy_docstring(Lyra2APRON.visit_DictDisplay)
    def visit_DictDisplay(self, expr: 'DictDisplay', environment=None, usub=False):
        assert not usub
        return PyTexpr1.cst(environment, PyMPQIntervalCoeff(PyMPQInterval.top()))

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
        vars = list()
        for variable in variables:
            vars.append(PyVar(variable.name))
        self.environment = PyEnvironment([], vars)
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
        self.state = self.state.assign(PyVar(left.name), expr)
        return self

    @copy_docstring(State._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'State':
        raise NotImplementedError(f"Assumption of {condition.__class__.__name__} is unsupported!")

    @copy_docstring(State._assume_binary_comparison)
    def _assume_binary_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'State':
        cond = self._lyra2apron.visit(condition, self.environment)
        abstract1 = self.domain(self.manager, self.environment, array=PyTcons1Array([cond]))
        self.state = self.state.meet(abstract1)
        return self

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

    @copy_docstring(State.output)
    def _output(self, output: Expression) -> 'APRONStateWithSummarization':
        return self  # nothing to be done

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'APRONStateWithSummarization':
        expr = self._lyra2apron.visit(right, self.environment)
        self.state = self.state.substitute(PyVar(left.name), expr)
        return self

    _negation_free = NegationFreeExpression()
    _lyra2apron = Lyra2APRONWithSummarization()
    manager: PyManager
