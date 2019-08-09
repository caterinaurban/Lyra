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
from typing import Set, Type

from apronpy.abstract1 import PyAbstract1
from apronpy.environment import PyEnvironment
from apronpy.linexpr1 import PyLinexpr1
from apronpy.manager import PyManager
from apronpy.tcons1 import PyTcons1Array, PyTcons1
from apronpy.texpr1 import PyTexpr1
from apronpy.var import PyVar

from lyra.abstract_domains.state import State
from lyra.core.expressions import VariableIdentifier, Expression, BinaryBooleanOperation, \
    BinaryComparisonOperation, NegationFreeExpression, Lyra2APRON
from lyra.core.utils import copy_docstring


class APRONState(State, metaclass=ABCMeta):
    """Analysis state based on APRON. An element of the abstract domain.

    Conjunction of constraints constraining the value of each variable.
    The value of all program variables is unconstrained by default.

    .. note:: Program variables storing collections are not supported yet.

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
    def _less_equal(self, other: 'APRONState') -> bool:
        return self.state <= other.state

    @copy_docstring(State._join)
    def _join(self, other: 'APRONState') -> 'APRONState':
        self.state = self.state.join(other.state)
        return self

    @copy_docstring(State._meet)
    def _meet(self, other: 'APRONState') -> 'APRONState':
        self.state = self.state.meet(other.state)
        return self

    @copy_docstring(State._widening)
    def _widening(self, other: 'APRONState') -> 'APRONState':
        self.state = self.state.widening(other.state)
        return self

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression) -> 'APRONState':
        if isinstance(left, VariableIdentifier):
            expr = self._lyra2apron.visit(right, self.environment)
            self.state = self.state.assign(PyVar(left.name), expr)
            return self
        raise NotImplementedError(f"Assignment to {left.__class__.__name__} is unsupported!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression, bwd: bool = False) -> 'APRONState':
        normal = self._negation_free.visit(condition)
        if isinstance(normal, BinaryBooleanOperation):
            if normal.operator == BinaryBooleanOperation.Operator.And:
                right = deepcopy(self)._assume(normal.right, bwd=bwd)
                return self._assume(normal.left, bwd=bwd).meet(right)
            if normal.operator == BinaryBooleanOperation.Operator.Or:
                right = deepcopy(self)._assume(normal.right, bwd=bwd)
                return self._assume(normal.left, bwd=bwd).join(right)
        elif isinstance(normal, BinaryComparisonOperation):
            cond = self._lyra2apron.visit(normal, self.environment)
            abstract1 = self.domain(self.manager, self.environment, array=PyTcons1Array([cond]))
            self.state = self.state.meet(abstract1)
            return self
        raise NotImplementedError(f"Assumption of {normal.__class__.__name__} is unsupported!")

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'APRONState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'APRONState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'APRONState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'APRONState':
        return self  # nothing to be done

    @copy_docstring(State.output)
    def _output(self, output: Expression) -> 'APRONState':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'APRONState':
        if isinstance(left, VariableIdentifier):
            expr = self._lyra2apron.visit(right, self.environment)
            self.state = self.state.substitute(PyVar(left.name), expr)
            return self
        raise NotImplementedError(f"Substitution of {left.__class__.__name__} is unsupported!")

    _negation_free = NegationFreeExpression()
    _lyra2apron = Lyra2APRON()
    manager: PyManager
