"""
Sign Lattice - Unit Tests
=========================

:Author: Jérôme Dohrau
"""
import unittest
from typing import List

from lyra.abstract_domains.numerical.sign_domain import SignLattice
from lyra.unittests.abstract_tests import ArithmeticLatticeTest


class TestSignLattice(unittest.TestCase, ArithmeticLatticeTest):

    def default(self):
        return SignLattice()

    @staticmethod
    def negative() -> 'SignLattice':
        return SignLattice(True, False, False)

    @staticmethod
    def positive() -> 'SignLattice':
        return SignLattice(False, True, False)

    @staticmethod
    def zero() -> 'SignLattice':
        return SignLattice(False, False, True)

    @staticmethod
    def non_negative() -> 'SignLattice':
        return SignLattice(False, True, True)

    @staticmethod
    def non_positive() -> 'SignLattice':
        return SignLattice(True, False, True)

    @staticmethod
    def non_zero() -> 'SignLattice':
        return SignLattice(True, True, False)

    def elements(self) -> List['SignLattice']:
        return [self.bottom(),
                self.top(),
                self.negative(),
                self.positive(),
                self.zero(),
                self.non_negative(),
                self.non_positive(),
                self.non_zero()]

    def test_less_equal(self):
        super().test_less_equal()

        self.assertTrue(self.negative().less_equal(self.non_positive()))
        self.assertFalse(self.non_negative().less_equal(self.negative()))
        self.assertTrue(self.positive().less_equal(self.non_negative()))
        self.assertFalse(self.non_negative().less_equal(self.positive()))
        self.assertFalse(self.zero().less_equal(self.non_zero()))
        self.assertFalse(self.non_zero().less_equal(self.zero()))

    def test_join(self):
        super().test_join()

        self.assertEqual(self.negative().join(self.positive()), self.non_zero())
        self.assertEqual(self.non_negative().join(self.non_positive()), self.top())

    def test_meet(self):
        super().test_meet()

        self.assertEqual(self.negative().meet(self.positive()), self.bottom())
        self.assertEqual(self.non_negative().meet(self.non_positive()), self.zero())

    def test_neg(self):
        super().test_neg()

        self.assertEqual(self.negative().neg(), self.positive())
        self.assertEqual(self.positive().neg(), self.negative())
        self.assertEqual(self.zero().neg(), self.zero())
        self.assertEqual(self.non_negative().neg(), self.non_positive())
        self.assertEqual(self.non_positive().neg(), self.non_negative())
        self.assertEqual(self.non_zero().neg(), self.non_zero())

    def test_add(self):
        super().test_add()

        self.assertEqual(self.positive().add(self.positive()), self.positive())
        self.assertEqual(self.non_negative().add(self.zero()), self.non_negative())
        self.assertEqual(self.negative().add(self.positive()), self.top())

    def test_sub(self):
        super().test_sub()

        self.assertEqual(self.positive().sub(self.negative()), self.positive())
        self.assertEqual(self.non_negative().sub(self.zero()), self.non_negative())
        self.assertEqual(self.positive().sub(self.positive()), self.top())

    def test_mult(self):
        super().test_mult()

        self.assertEqual(self.positive().mult(self.positive()), self.positive())
        self.assertEqual(self.positive().mult(self.non_negative()), self.non_negative())
        self.assertEqual(self.negative().mult(self.positive()), self.negative())
        self.assertEqual(self.negative().mult(self.zero()), self.zero())


if __name__ == '__main__':
    unittest.main()
