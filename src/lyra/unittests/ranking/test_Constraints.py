import unittest

from apronpy.coeff import PyMPQScalarCoeff
from apronpy.environment import PyEnvironment
from apronpy.lincons0 import ConsTyp
from apronpy.lincons1 import PyLincons1
from apronpy.linexpr1 import PyLinexpr1
from apronpy.scalar import PyMPQScalar
from apronpy.var import PyVar

from lyra.abstract_domains.ranking.contraints import ApronBoxConstraint, \
    ParityConstraint, Constraint


class TestApronBoxConstraints(unittest.TestCase):

    def test_bottom(self):
        bottom = ApronBoxConstraint.bottom()
        self.assertFalse(bottom.type == Constraint.Type.Parity)
        self.assertTrue(bottom.type == Constraint.Type.Linear)
        self.assertEqual(str(bottom), 'false')
        self.assertTrue(bottom.is_bottom())
        self.assertFalse(bottom.is_top())

    def test_constraint(self):
        x = PyVar('x')
        y = PyVar('y')
        env = PyEnvironment([x, y])
        e = PyLinexpr1(env)
        e.set_coeff(x, PyMPQScalarCoeff(1))
        e.set_cst(PyMPQScalarCoeff(-3))
        c = ApronBoxConstraint(PyLincons1(ConsTyp.AP_CONS_SUPEQ, e))
        self.assertFalse(c.type == Constraint.Type.Parity)
        self.assertTrue(c.type == Constraint.Type.Linear)
        self.assertEqual(str(c), 'x >= 3')

    def test_top(self):
        top = ApronBoxConstraint.top()
        self.assertFalse(top.type == Constraint.Type.Parity)
        self.assertTrue(top.type == Constraint.Type.Linear)
        self.assertEqual(str(top), 'true')
        self.assertFalse(top.is_bottom())
        self.assertTrue(top.is_top())

    def test_negation(self):
        x = PyVar('x')
        y = PyVar('y')
        env = PyEnvironment([x, y])
        e = PyLinexpr1(env)
        e.set_coeff(x, PyMPQScalarCoeff(1))
        e.set_cst(PyMPQScalarCoeff(-3))
        c = ApronBoxConstraint(PyLincons1(ConsTyp.AP_CONS_SUPEQ, e)).negate()
        self.assertFalse(c.type == Constraint.Type.Parity)
        self.assertTrue(c.type == Constraint.Type.Linear)
        self.assertEqual(str(c), 'x <= 2')


class TestParityConstraints(unittest.TestCase):

    def test_constraint(self):
        x = PyVar('x')
        y = PyVar('y')
        env = PyEnvironment([x, y])
        e = PyLinexpr1(env)
        e.set_coeff(x, PyMPQScalarCoeff(1))
        e.set_cst(PyMPQScalarCoeff(0))
        k = PyMPQScalar(2)
        l = PyLincons1(ConsTyp.AP_CONS_EQMOD, e, k)
        c = ParityConstraint(l)
        self.assertTrue(c.type == Constraint.Type.Parity)
        self.assertFalse(c.type == Constraint.Type.Linear)
        self.assertEqual(str(c), 'x % 2 = 0')

    def test_negation(self):
        x = PyVar('x')
        y = PyVar('y')
        env = PyEnvironment([x, y])
        e = PyLinexpr1(env)
        e.set_coeff(x, PyMPQScalarCoeff(1))
        e.set_cst(PyMPQScalarCoeff(0))
        k = PyMPQScalar(2)
        c = ParityConstraint(PyLincons1(ConsTyp.AP_CONS_EQMOD, e, k)).negate()
        self.assertTrue(c.type == Constraint.Type.Parity)
        self.assertFalse(c.type == Constraint.Type.Linear)
        self.assertEqual(str(c), 'x % 2 = 1')


if __name__ == '__main__':
    unittest.main()
