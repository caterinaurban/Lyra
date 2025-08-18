from copy import deepcopy
from typing import Dict, List

from apronpy.abstract1 import PyAbstract1
from apronpy.box import PyBox, PyBoxMPQManager
from apronpy.coeff import PyMPQScalarCoeff
from apronpy.environment import PyEnvironment
from apronpy.interval import PyInterval
from apronpy.lincons0 import ConsTyp
from apronpy.lincons1 import PyLincons1, PyLincons1Array
from apronpy.linexpr1 import PyLinexpr1
from apronpy.manager import PyManager
from apronpy.oct import PyOctMPQManager, PyOct
from apronpy.polka import PyPolkaMPQlooseManager, PyPolka
from apronpy.scalar import PyMPQScalar
from apronpy.var import PyVar

from lyra.abstract_domains.ranking.contraints import Constraint, \
    LinearConstraint, ParityConstraint, ApronPolyConstraint, ApronBoxConstraint


class Partition:

    def __init__(self, environment: PyEnvironment):
        self._environment = environment
        self._constraints: Dict[Constraint.Type, List[Constraint]] = dict()
        self._constraints[Constraint.Type.Parity] = list()
        self._constraints[Constraint.Type.Linear] = list()
        self._manager = None

    @property
    def environment(self):
        return self._environment

    @property
    def constraints(self) -> Dict[Constraint.Type, List[Constraint]]:
        return self._constraints

    @property
    def parity_constraints(self) -> List[Constraint]:
        return self._constraints[Constraint.Type.Parity]

    @property
    def linear_constraints(self) -> List[Constraint]:
        return self._constraints[Constraint.Type.Linear]

    def _partition2pyabstract1(self) -> PyAbstract1:
        constraints = [c.constraint for c in self.linear_constraints]
        a = PyLincons1Array(constraints, self._environment)
        if self._manager == PyBoxMPQManager:
            pyabstract1 = PyBox(self._manager(), self._environment, array=a)
        elif self._manager == PyOctMPQManager:
            pyabstract1 = PyOct(self._manager(), self._environment, array=a)
        else:
            assert self._manager == PyPolkaMPQlooseManager
            pyabstract1 = PyPolka(self._manager(), self._environment, array=a)
        return pyabstract1

    def add_constraint(self, constraint: Constraint):
        if constraint.type == Constraint.Type.Parity:
            self.parity_constraints.append(constraint)
        else:
            assert constraint.type == Constraint.Type.Linear
            # identify the least precise manager that can handle the constraints
            assert isinstance(constraint, LinearConstraint)
            box_kind = constraint.kind == LinearConstraint.Kind.Box
            oct_kind = constraint.kind == LinearConstraint.Kind.Oct
            oct_man = self._manager and self._manager == PyOctMPQManager
            poly_man = self._manager and self._manager == PyPolkaMPQlooseManager
            if box_kind and not oct_man and not poly_man:
                self._manager = PyBoxMPQManager
            elif oct_kind and not poly_man:
                self._manager = PyOctMPQManager
            elif constraint.kind == LinearConstraint.Kind.Poly:
                self._manager = PyPolkaMPQlooseManager
            self.linear_constraints.append(constraint)

    def is_bottom(self):
        p: PyAbstract1 = self._partition2pyabstract1()
        if p.is_bottom():
            return True
        result = False
        for parity in self.parity_constraints:
            assert isinstance(parity, ParityConstraint)
            itv: PyInterval = p.bound_linexpr(parity.linexpr)
            inf = itv.interval.contents.inf.contents
            sup = itv.interval.contents.sup.contents
            minf = PyMPQScalar.init_infty(-1).scalar.contents
            pinf = PyMPQScalar.init_infty(1).scalar.contents
            if inf != minf and sup != pinf:
                exists = False
                for i in range(int(str(inf)), int(str(sup)) + 1):
                    even = parity.is_even() and i % 2 == 0
                    odd = parity.is_odd() and i % 2 == 1
                    if even or odd:
                        exists = True
                result = result or not exists
        return result

    def __repr__(self):
        if self.is_bottom():
            return '⊥'
        parity = ' ∧ '.join(str(parity) for parity in self.parity_constraints)
        linear = ' ∧ '.join(str(linear) for linear in self.linear_constraints)
        return '{} ∧ {}'.format(parity, linear)


# x = PyVar('x')
# y = PyVar('y')
# env = PyEnvironment([x, y])
#
# p = Partition(env)
#
# e1 = PyLinexpr1(env)
# e1.set_coeff(x, PyMPQScalarCoeff(1))
# e1.set_cst(PyMPQScalarCoeff(1))
# k = PyMPQScalar(2)
# c1 = PyLincons1(ConsTyp.AP_CONS_EQMOD, e1, k)   # x is odd
# cc1 = ParityConstraint(c1)
#
# p.add_constraint(cc1)
#
# e2 = PyLinexpr1(env)
# e2.set_coeff(x, PyMPQScalarCoeff(1))
# e2.set_cst(PyMPQScalarCoeff(-1))
# c2 = PyLincons1(ConsTyp.AP_CONS_SUPEQ, e2)     # x >= 1
# cc2 = ApronBoxConstraint(c2)
#
# p.add_constraint(cc2)
#
# e3 = PyLinexpr1(env)
# e3.set_coeff(x, PyMPQScalarCoeff(-1))
# e3.set_cst(PyMPQScalarCoeff(1))
# c3 = PyLincons1(ConsTyp.AP_CONS_SUPEQ, e3)     # x <= 1
# cc3 = ApronPolyConstraint(c3)
#
# p.add_constraint(cc3)
#
# print(p)
#
# print(p.is_bottom())

# a = PyLincons1Array([c1, c2], env)
# p1 = PyPolka(PyPolkaMPQlooseManager(), env, array=a)
# print('p1: ', p1)
# p2 = PyBox(PyBoxMPQManager(), env, array=a)
# print('p2: ', p2)
