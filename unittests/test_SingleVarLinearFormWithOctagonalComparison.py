import unittest

from abstract_domains.numerical.octagon_domain import OctagonLattice
from abstract_domains.segmentation.bounds import SingleVarLinearFormWithOctagonalComparison
from core.expressions import *
from core.expressions_tools import MINUS, PLUS


class TestSingleVarLinearFormWithOctagonalComparison(unittest.TestCase):
    def runTest(self):
        a = VariableIdentifier(int, 'a')
        b = VariableIdentifier(int, 'b')

        a_plus_5 = BinaryArithmeticOperation(int, a, BinaryArithmeticOperation.Operator.Add, Literal(int, '5'))
        a_plus_7 = BinaryArithmeticOperation(int, a, BinaryArithmeticOperation.Operator.Add, Literal(int, '7'))
        b_minus_1 = BinaryArithmeticOperation(int, b, BinaryArithmeticOperation.Operator.Sub, Literal(int, '1'))
        b_minus_2 = BinaryArithmeticOperation(int, b, BinaryArithmeticOperation.Operator.Sub, Literal(int, '2'))
        c1 = Literal(int, '1')

        octagon = OctagonLattice([a, b])

        # check with no relational constraints
        f1 = SingleVarLinearFormWithOctagonalComparison.from_expression(a_plus_5)
        f2 = SingleVarLinearFormWithOctagonalComparison.from_expression(a_plus_7)
        self.assertTrue(f1.lt_octagonal(f2, octagon))

        # check interval constraints
        octagon.set_bounds(a, -10, -5)
        f_constant = SingleVarLinearFormWithOctagonalComparison.from_expression(c1)
        self.assertTrue(f1.lt_octagonal(f_constant,octagon))

        # check relational constraints
        octagon.set_octagonal_constraint(PLUS, a, MINUS, b, -2)  # a - b <= -2 ("a is at least 2 smaller than b")
        f1 = SingleVarLinearFormWithOctagonalComparison.from_expression(a)
        f2 = SingleVarLinearFormWithOctagonalComparison.from_expression(b_minus_1)
        self.assertTrue(f1.lt_octagonal(f2, octagon))

        # check relational constraints (corner case)
        octagon.set_octagonal_constraint(PLUS, a, MINUS, b, -2)  # a - b <= -2 ("a is at least 2 smaller than b")
        f1 = SingleVarLinearFormWithOctagonalComparison.from_expression(a)
        f2 = SingleVarLinearFormWithOctagonalComparison.from_expression(b_minus_2)
        self.assertTrue(f1.le_octagonal(f2, octagon))
        self.assertFalse(f1.lt_octagonal(f2, octagon))

        # forget relational constraint again and see if cannot not infer property f1 <= f2 anymore
        octagon.forget(a)
        self.assertFalse(f1.le_octagonal(f2, octagon))


def suite():
    s = unittest.TestSuite()
    s.addTest(TestSingleVarLinearFormWithOctagonalComparison())
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
