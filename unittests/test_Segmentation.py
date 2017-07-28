import unittest

from abstract_domains.numerical.octagon_domain import OctagonLattice
from abstract_domains.segmentation.segmentation import SegmentedListLattice, Limit
from abstract_domains.usage.used import UsedLattice, Used
from core.expressions import *
from abstract_domains.segmentation.bounds import SingleVarLinearFormWithOctagonalComparison
from core.expressions_tools import PLUS, MINUS


class TestSegmentationUnification(unittest.TestCase):
    def runTest(self):
        i = VariableIdentifier(int, 'i')  # i is an index variable
        n = VariableIdentifier(int, 'n')  # n is used as the length of the list
        x = VariableIdentifier(int, 'x')  # we know nothing about x and y except that they are equal
        y = VariableIdentifier(int, 'y')
        c0 = Literal(int, '0')
        c1 = Literal(int, '1')

        octagon = OctagonLattice([i, n, x, y])

        s1 = SegmentedListLattice(n, UsedLattice, octagon)
        s1.limits[0].bounds.add(SingleVarLinearFormWithOctagonalComparison.from_expression(i))
        s1.possibly_empty[0] = False

        s2 = SegmentedListLattice(n, UsedLattice, octagon)
        i_minus_1 = BinaryArithmeticOperation(int, i, BinaryArithmeticOperation.Operator.Sub, c1)
        s2.limits[0].bounds.add(SingleVarLinearFormWithOctagonalComparison.from_expression(i_minus_1))
        s2.add_limit(0, Limit({SingleVarLinearFormWithOctagonalComparison.from_expression(c1),
                               SingleVarLinearFormWithOctagonalComparison.from_expression(i)}),
                     predicate_before=UsedLattice(Used.S))
        s2.possibly_empty[0] = False

        print("Original:")
        print(s1)
        print(s2)

        s1.unify(s2, lambda: UsedLattice().top())
        print("\nUnified:")
        print(s1)
        print(s2)

        print("\nJoined:")
        s1.join(s2)
        print(s1)

        print("\nSet unused at index i:")
        s1.set_predicate(i, UsedLattice(Used.N))
        print(s1)

        print("\nSet scoped at from start of list to (i+1) exclusive:")
        i_plus_1 = BinaryArithmeticOperation(int, i, BinaryArithmeticOperation.Operator.Add, c1)
        s1._set_predicate_in_form_range(SingleVarLinearFormWithOctagonalComparison.from_expression(c0),
                                        SingleVarLinearFormWithOctagonalComparison.from_expression(i_plus_1),
                                        UsedLattice(Used.S))
        print(s1)

        print("\nSet overwritten at unknown location x:")
        s1.set_predicate(x, UsedLattice(Used.O))
        print(s1)

        print("\nSet used at unknown location y (equals x):")
        # set x equals y in octagon
        octagon.set_octagonal_constraint(PLUS, x, MINUS, y, 0)
        octagon.set_octagonal_constraint(MINUS, x, PLUS, y, 0)
        s1.set_predicate(y, UsedLattice(Used.U))
        print(s1)


def suite():
    s = unittest.TestSuite()
    s.addTest(TestSegmentationUnification())
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
