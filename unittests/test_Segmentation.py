import unittest

from abstract_domains.numerical.octagon_domain import OctagonLattice
from abstract_domains.segmentation.bounds import SingleVarLinearFormWithOctagonalComparison
from abstract_domains.segmentation.segmentation import Segmentation, Limit
from abstract_domains.usage.used import UsedLattice, Used
from core.expressions import *
from core.expressions_tools import MINUS, PLUS
from abstract_domains.segmentation.bounds import SingleVarLinearFormWithOctagonalComparison as Form


class TestSegmentationUnification(unittest.TestCase):
    def runTest(self):
        i = VariableIdentifier(int, 'i')
        n = VariableIdentifier(int, 'n')
        c0 = Literal(int, '0')
        c1 = Literal(int, '1')

        octagon = OctagonLattice([i, n])

        s1 = Segmentation(n, UsedLattice, octagon)
        s1.limits[0].bounds.add(Form(i, octagon))
        s1.possibly_empty[0] = False

        s2 = Segmentation(n, UsedLattice, octagon)
        i_minus_1 = BinaryArithmeticOperation(int, i, BinaryArithmeticOperation.Operator.Sub, c1)
        s2.limits[0].bounds.add(Form(i_minus_1, octagon))
        s2.add_limit(0, Limit({Form(c1, octagon), Form(i, octagon)}), predicate_before=UsedLattice(Used.S))
        s2.possibly_empty[0] = False

        print(s1)
        print(s2)

        s1.unify(s2, lambda: UsedLattice().top())
        print(s1)
        print(s2)


def suite():
    s = unittest.TestSuite()
    s.addTest(TestSegmentationUnification())
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
