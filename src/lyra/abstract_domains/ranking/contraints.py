from abc import ABCMeta, abstractmethod
from copy import deepcopy
from enum import Enum

from apronpy.coeff import PyMPQScalarCoeff
from apronpy.environment import PyEnvironment
from apronpy.lincons0 import ConsTyp
from apronpy.lincons1 import PyLincons1
from apronpy.linexpr1 import PyLinexpr1
from apronpy.mpq import PyMPQ
from apronpy.scalar import PyMPQScalar
from apronpy.var import PyVar


class Constraint(metaclass=ABCMeta):

    class Type(Enum):
        Parity = 0
        Linear = 1

    def __init__(self, type: Type, constraint: PyLincons1):
        self._type = type
        assert constraint.lincons1.env.contents.realdim == 0
        self._constraint = constraint
        self._negation = None

    @property
    def type(self):
        return self._type

    @property
    def constraint(self) -> PyLincons1:
        return self._constraint

    @property
    def linexpr(self) -> PyLinexpr1:
        vars, coeffs = list(), list()
        env = self._constraint.lincons1.env
        for i in range(env.contents.intdim):
            var = PyVar(env.contents.var_of_dim[i].decode('utf-8'))
            vars.append(var)
            coeffs.append(self._constraint.get_coeff(var))
        expr = PyLinexpr1(PyEnvironment(vars))
        for var, coeff in zip(vars, coeffs):
            expr.set_coeff(var, coeff)
        return expr

    @property
    def constant(self) -> PyMPQScalarCoeff:
        return self._constraint.get_cst()

    @property
    def negation(self) -> PyLincons1:
        return self._negation

    def negate(self):
        self._constraint, self._negation = self._negation, self._constraint
        return self

    def linexpr2str(self, negate=False) -> str:
        expr = list()
        env = self._constraint.lincons1.env
        for i in range(env.contents.intdim):
            var = PyVar(env.contents.var_of_dim[i].decode('utf-8'))
            coeff = self._constraint.get_coeff(var)
            if coeff != PyMPQScalarCoeff(0):
                if negate:
                    if coeff == PyMPQScalarCoeff(-1):
                        expr.append('{}'.format(var))
                    else:
                        expr.append('{}·{}'.format(-coeff, var))
                else:
                    if coeff == PyMPQScalarCoeff(1):
                        expr.append('{}'.format(var))
                    else:
                        expr.append('{}·{}'.format(coeff, var))
        return ' + '.join(expr).replace('+ -', '- ')

    @abstractmethod
    def __repr__(self):
        pass


class ParityConstraint(Constraint):

    def __init__(self, constraint: PyLincons1):
        assert constraint.lincons1.lincons0.constyp == ConsTyp.AP_CONS_EQMOD
        # assert str(constraint.lincons1.lincons0.scalar.contents) == '2'
        super().__init__(Constraint.Type.Parity, constraint)
        # build negated constraint
        negation = deepcopy(constraint)
        cst = self._constraint.get_cst()
        if cst == PyMPQScalarCoeff(0):
            negation.set_cst(PyMPQScalarCoeff(1))
        else:
            assert cst == PyMPQScalarCoeff(1)
            negation.set_cst(PyMPQScalarCoeff(0))
        self._negation = negation

    def is_even(self):
        return self._constraint.get_cst() == PyMPQScalarCoeff(0)

    def is_odd(self):
        return self._constraint.get_cst() == PyMPQScalarCoeff(1)

    def __repr__(self):
        cst = self._constraint.get_cst()
        k = self._constraint.lincons1.lincons0.scalar.contents
        return '{} % {} = {}'.format(self.linexpr2str(), k, cst)


class LinearConstraint(Constraint, metaclass=ABCMeta):

    class Kind(Enum):
        Box = 0
        Oct = 1
        Poly = 2

    kind: Kind = None

    def __init__(self, constraint: PyLincons1):
        assert constraint.lincons1.lincons0.constyp == ConsTyp.AP_CONS_SUPEQ
        super().__init__(Constraint.Type.Linear, constraint)
        # build negated constraint
        env = constraint.lincons1.env
        negation = deepcopy(constraint)
        for i in range(env.contents.intdim):
            var = PyVar(env.contents.var_of_dim[i].decode('utf-8'))
            negation.set_coeff(var, -negation.get_coeff(var))
        cst = negation.get_cst()
        k = cst.coeff.contents.val.scalar.contents
        if k.discr == 0:
            value = PyMPQ(k.val.dbl)
        elif k.discr == 1:
            value = PyMPQ(k.val.mpq_ptr.contents)
        else:
            assert k.discr == 2
            value = PyMPQ(k.val.mpfr_ptr.contents)
        negation.set_cst(PyMPQScalarCoeff(-value - PyMPQ(1)))
        self._negation = negation

    @classmethod
    def bottom(cls):
        expr = PyLinexpr1(PyEnvironment())
        constraint = PyLincons1(ConsTyp.AP_CONS_SUPEQ, expr)
        constraint.set_cst(PyMPQScalarCoeff(-1))
        return cls(constraint)

    @classmethod
    def top(cls):
        expr = PyLinexpr1(PyEnvironment())
        constraint = PyLincons1(ConsTyp.AP_CONS_SUPEQ, expr)
        return cls(constraint)

    def is_bottom(self) -> bool:
        return self._constraint.is_unsat()

    def is_top(self) -> bool:
        return self._negation.is_unsat()

    def __repr__(self):
        if self.is_bottom():
            return 'false'
        elif self.is_top():
            return 'true'
        else:
            cst = self._constraint.get_cst()
            if cst < PyMPQScalarCoeff(0):
                return '{} >= {}'.format(self.linexpr2str(), -cst)
            else:
                return '{} <= {}'.format(self.linexpr2str(negate=True), cst)


class ApronBoxConstraint(LinearConstraint):

    kind: LinearConstraint.Kind = LinearConstraint.Kind.Box


class ApronOctConstraint(LinearConstraint):

    kind: LinearConstraint.Kind = LinearConstraint.Kind.Oct


class ApronPolyConstraint(LinearConstraint):

    kind: LinearConstraint.Kind = LinearConstraint.Kind.Poly


# x = PyVar('x')
# y = PyVar('y')
# env = PyEnvironment([x, y])
# e = PyLinexpr1(env)
# e.set_coeff(x, PyMPQScalarCoeff(1))
# e.set_cst(PyMPQScalarCoeff(0))
# k = PyMPQScalar(2)
# l = PyLincons1(ConsTyp.AP_CONS_EQMOD, e, k)
# print(l)
