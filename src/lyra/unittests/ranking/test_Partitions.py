import unittest

from apronpy.coeff import PyMPQScalarCoeff
from apronpy.environment import PyEnvironment
from apronpy.lincons0 import ConsTyp
from apronpy.lincons1 import PyLincons1
from apronpy.linexpr1 import PyLinexpr1
from apronpy.scalar import PyMPQScalar
from apronpy.var import PyVar

from lyra.abstract_domains.ranking.contraints import ParityConstraint, \
    ApronBoxConstraint, ApronPolyConstraint
from lyra.abstract_domains.ranking.partitions import Partition


class TestPartitions(unittest.TestCase):

    def test_bottom(self):
        x = PyVar('x')
        y = PyVar('y')
        env = PyEnvironment([x, y])
        p = Partition(env)
        e1 = PyLinexpr1(env)
        e1.set_coeff(x, PyMPQScalarCoeff(1))
        k = PyMPQScalar(2)
        c1 = PyLincons1(ConsTyp.AP_CONS_EQMOD, e1, k)  # x is even
        cc1 = ParityConstraint(c1)
        p.add_constraint(cc1)
        e2 = PyLinexpr1(env)
        e2.set_coeff(x, PyMPQScalarCoeff(1))
        e2.set_cst(PyMPQScalarCoeff(-1))
        c2 = PyLincons1(ConsTyp.AP_CONS_SUPEQ, e2)  # x >= 1
        cc2 = ApronBoxConstraint(c2)
        p.add_constraint(cc2)
        e3 = PyLinexpr1(env)
        e3.set_coeff(x, PyMPQScalarCoeff(-1))
        e3.set_cst(PyMPQScalarCoeff(1))
        c3 = PyLincons1(ConsTyp.AP_CONS_SUPEQ, e3)  # x <= 1
        cc3 = ApronPolyConstraint(c3)
        p.add_constraint(cc3)
        self.assertEqual(str(p), '⊥')
        self.assertTrue(p.is_bottom())

    def test_repr(self):
        x = PyVar('x')
        y = PyVar('y')
        env = PyEnvironment([x, y])
        p = Partition(env)
        e1 = PyLinexpr1(env)
        e1.set_coeff(x, PyMPQScalarCoeff(1))
        e1.set_cst(PyMPQScalarCoeff(1))
        k = PyMPQScalar(2)
        c1 = PyLincons1(ConsTyp.AP_CONS_EQMOD, e1, k)  # x is odd
        cc1 = ParityConstraint(c1)
        p.add_constraint(cc1)
        e2 = PyLinexpr1(env)
        e2.set_coeff(x, PyMPQScalarCoeff(1))
        e2.set_cst(PyMPQScalarCoeff(-1))
        c2 = PyLincons1(ConsTyp.AP_CONS_SUPEQ, e2)  # x >= 1
        cc2 = ApronBoxConstraint(c2)
        p.add_constraint(cc2)
        e3 = PyLinexpr1(env)
        e3.set_coeff(x, PyMPQScalarCoeff(-1))
        e3.set_cst(PyMPQScalarCoeff(1))
        c3 = PyLincons1(ConsTyp.AP_CONS_SUPEQ, e3)  # x <= 1
        cc3 = ApronPolyConstraint(c3)
        p.add_constraint(cc3)
        self.assertEqual(str(p), 'x % 2 = 1 ∧ x >= 1 ∧ x <= 1')


if __name__ == '__main__':
    unittest.main()