"""
Polyhedra Abstract Domain
=========================

Relational abstract domain to be used for **numerical analysis**.
The set of possible numerical values of a program variable in a program state
is represented by a conjunction of linear constraints.

:Authors: Caterina Urban
"""
from copy import deepcopy
from typing import Set, Union

from apronpy.coeff import PyMPQScalarCoeff, PyMPQIntervalCoeff
from apronpy.environment import PyEnvironment
from apronpy.interval import PyMPQInterval
from apronpy.lincons0 import ConsTyp
from apronpy.polka import PyPolkaMPQstrict
from apronpy.tcons1 import PyTcons1Array, PyTcons1
from apronpy.texpr0 import TexprOp, TexprRtype, TexprRdir
from apronpy.texpr1 import PyTexpr1
from apronpy.var import PyVar

from lyra.abstract_domains.state import State
from lyra.core.expressions import VariableIdentifier, Expression, BinaryBooleanOperation, \
    BinaryComparisonOperation, NegationFreeExpression, Literal, Input, UnaryArithmeticOperation, \
    BinaryArithmeticOperation
from lyra.core.utils import copy_docstring


def lyra2apron(environment, expression: Expression, usub = False) -> Union[PyTexpr1, PyTcons1]:
    if isinstance(expression, Literal):
        if usub:
            cst = PyMPQScalarCoeff(-float(expression.val))
        else:
            cst = PyMPQScalarCoeff(float(expression.val))
        return PyTexpr1.cst(environment, cst)
    elif isinstance(expression, VariableIdentifier):
        assert not usub
        variable = PyVar(expression.name)
        return PyTexpr1.var(environment, variable)
    elif isinstance(expression, Input):
        assert not usub
        expr = PyMPQIntervalCoeff(PyMPQInterval.top())
        return PyTexpr1.cst(environment, expr)
    elif isinstance(expression, UnaryArithmeticOperation):
        usub = expression.operator == UnaryArithmeticOperation.Operator.Sub
        return lyra2apron(environment, expression.expression, usub)
    elif isinstance(expression, BinaryArithmeticOperation):
        assert not usub
        expr1 = lyra2apron(environment, expression.left)
        expr2 = lyra2apron(environment, expression.right)
        op2op = {
            BinaryArithmeticOperation.Operator.Add: TexprOp.AP_TEXPR_ADD,
            BinaryArithmeticOperation.Operator.Sub: TexprOp.AP_TEXPR_SUB,
            BinaryArithmeticOperation.Operator.Mult: TexprOp.AP_TEXPR_MUL,
            BinaryArithmeticOperation.Operator.Div: TexprOp.AP_TEXPR_DIV
        }
        op = op2op[expression.operator]
        return PyTexpr1.binop(op, expr1, expr2, TexprRtype.AP_RTYPE_REAL, TexprRdir.AP_RDIR_RND)
    elif isinstance(expression, BinaryComparisonOperation):
        assert not usub
        # assert expression.left.typ == expression.right.typ
        typ = expression.left.typ
        left = expression.left
        right = expression.right
        sub = BinaryArithmeticOperation.Operator.Sub
        if expression.operator == BinaryComparisonOperation.Operator.GtE:
            expr = lyra2apron(environment, BinaryArithmeticOperation(typ, left, sub, right))
            return PyTcons1.make(expr, ConsTyp.AP_CONS_SUPEQ)
        elif expression.operator == BinaryComparisonOperation.Operator.Gt:
            expr = lyra2apron(environment, BinaryArithmeticOperation(typ, left, sub, right))
            return PyTcons1.make(expr, ConsTyp.AP_CONS_SUP)
        elif expression.operator == BinaryComparisonOperation.Operator.LtE:
            expr = lyra2apron(environment, BinaryArithmeticOperation(typ, right, sub, left))
            return PyTcons1.make(expr, ConsTyp.AP_CONS_SUPEQ)
        elif expression.operator == BinaryComparisonOperation.Operator.Lt:
            expr = lyra2apron(environment, BinaryArithmeticOperation(typ, right, sub, left))
            return PyTcons1.make(expr, ConsTyp.AP_CONS_SUP)
    raise NotImplementedError(f"lyra2apron conversion for {expression} is not yet supported!")


class PolyhedraState(State):
    """Polyhedra analysis state. An element of the polyhedra abstract domain.

    Conjunction of linear constraints constraining the value of each variable.
    The value of all program variables is unconstrained by default.

    .. note:: Program variables storing collections are abstracted via summarization.

    .. document private methods
    .. automethod:: PolyhedraState._assign
    .. automethod:: PolyhedraState._assume
    .. automethod:: PolyhedraState._output
    .. automethod:: PolyhedraState._substitute

    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        super().__init__(precursory=precursory)
        r_vars = list()
        for variable in variables:
            r_vars.append(PyVar(variable.name))
        self.environment = PyEnvironment([], r_vars)
        self.polka = PyPolkaMPQstrict(self.environment)

    @copy_docstring(State.bottom)
    def bottom(self):
        self.polka = PyPolkaMPQstrict.bottom(self.environment)
        return self

    @copy_docstring(State.top)
    def top(self):
        self.polka = PyPolkaMPQstrict.top(self.environment)
        return self

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return str(self.polka)

    @copy_docstring(State.is_bottom)
    def is_bottom(self) -> bool:
        return self.polka.is_bottom()

    @copy_docstring(State.is_top)
    def is_top(self) -> bool:
        return self.polka.is_top()

    @copy_docstring(State._less_equal)
    def _less_equal(self, other: 'PolyhedraState') -> bool:
        return self.polka <= other.polka

    @copy_docstring(State._join)
    def _join(self, other: 'PolyhedraState') -> 'PolyhedraState':
        self.polka = self.polka.join(other.polka)
        return self

    @copy_docstring(State._meet)
    def _meet(self, other: 'PolyhedraState') -> 'PolyhedraState':
        self.polka = self.polka.meet(other.polka)
        return self

    @copy_docstring(State._widening)
    def _widening(self, other: 'PolyhedraState') -> 'PolyhedraState':
        self.polka = self.polka.widening(other.polka)
        return self

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression) -> 'PolyhedraState':
        if isinstance(left, VariableIdentifier):
            expr = lyra2apron(self.environment, right)
            self.polka = self.polka.assign(PyVar(left.name), expr)
            return self
        raise NotImplementedError(f"Assignment to {left.__class__.__name__} is unsupported!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression, bwd: bool = False) -> 'PolyhedraState':
        normal = NegationFreeExpression().visit(condition)
        if isinstance(normal, BinaryBooleanOperation):
            if normal.operator == BinaryBooleanOperation.Operator.And:
                right = deepcopy(self)._assume(normal.right, bwd=bwd)
                return self._assume(normal.left, bwd=bwd).meet(right)
            if normal.operator == BinaryBooleanOperation.Operator.Or:
                right = deepcopy(self)._assume(normal.right, bwd=bwd)
                return self._assume(normal.left, bwd=bwd).join(right)
        elif isinstance(normal, BinaryComparisonOperation):
            cond = lyra2apron(self.environment, normal)
            self.polka = self.polka.meet(PyTcons1Array([cond.tcons1]))
            return self
        raise NotImplementedError(f"Assumption of {normal.__class__.__name__} is unsupported!")

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'PolyhedraState':
        return self     # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'PolyhedraState':
        return self     # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'PolyhedraState':
        return self     # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'PolyhedraState':
        return self     # nothing to be done

    @copy_docstring(State.output)
    def _output(self, output: Expression) -> 'PolyhedraState':
        return self     # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'PolyhedraState':
        if isinstance(left, VariableIdentifier):
            expr = lyra2apron(self.environment, right)
            self.polka = self.polka.substitute(PyVar(left.name), expr)
            return self
        raise NotImplementedError(f"Substitution of {left.__class__.__name__} is unsupported!")
