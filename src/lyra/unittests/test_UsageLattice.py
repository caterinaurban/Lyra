"""
Usage Lattice - Unit Tests
==========================

:Author: Caterina Urban
"""


import unittest
from lyra.abstract_domains.usage.usage_lattice import UsageLattice

U = UsageLattice.Status.U
S = UsageLattice.Status.S
W = UsageLattice.Status.W
N = UsageLattice.Status.N


class TestUsageLattice(unittest.TestCase):

    def test_init(self):
        self.assertTrue(UsageLattice().is_bottom())
        self.assertFalse(UsageLattice().is_top())

        self.assertFalse(UsageLattice(W).is_bottom())
        self.assertFalse(UsageLattice(W).is_top())

        self.assertFalse(UsageLattice(S).is_bottom())
        self.assertFalse(UsageLattice(S).is_top())

        self.assertFalse(UsageLattice(U).is_bottom())
        self.assertTrue(UsageLattice(U).is_top())

    def test_leq(self):
        self.assertTrue(UsageLattice().less_equal(UsageLattice(S)))
        self.assertTrue(UsageLattice().less_equal(UsageLattice(W)))
        self.assertTrue(UsageLattice().less_equal(UsageLattice(U)))

        self.assertFalse(UsageLattice(S).less_equal(UsageLattice()))
        self.assertFalse(UsageLattice(S).less_equal(UsageLattice(W)))
        self.assertTrue(UsageLattice(S).less_equal(UsageLattice(U)))

        self.assertFalse(UsageLattice(W).less_equal(UsageLattice()))
        self.assertFalse(UsageLattice(W).less_equal(UsageLattice(S)))
        self.assertTrue(UsageLattice(W).less_equal(UsageLattice(U)))

        self.assertFalse(UsageLattice(U).less_equal(UsageLattice()))
        self.assertFalse(UsageLattice(U).less_equal(UsageLattice(S)))
        self.assertFalse(UsageLattice(U).less_equal(UsageLattice(W)))

    def test_join(self):
        self.assertEqual(UsageLattice().join(UsageLattice(S)), UsageLattice(S))
        self.assertEqual(UsageLattice().join(UsageLattice(W)), UsageLattice(W))
        self.assertEqual(UsageLattice().join(UsageLattice(U)), UsageLattice(U))

        self.assertEqual(UsageLattice(S).join(UsageLattice()), UsageLattice(S))
        self.assertEqual(UsageLattice(S).join(UsageLattice(W)), UsageLattice(U))
        self.assertEqual(UsageLattice(S).join(UsageLattice(U)), UsageLattice(U))

        self.assertEqual(UsageLattice(W).join(UsageLattice()), UsageLattice(W))
        self.assertEqual(UsageLattice(W).join(UsageLattice(S)), UsageLattice(U))
        self.assertEqual(UsageLattice(W).join(UsageLattice(U)), UsageLattice(U))

        self.assertEqual(UsageLattice(U).join(UsageLattice()), UsageLattice(U))
        self.assertEqual(UsageLattice(U).join(UsageLattice(S)), UsageLattice(U))
        self.assertEqual(UsageLattice(U).join(UsageLattice(W)), UsageLattice(U))

    def test_meet(self):
        self.assertEqual(UsageLattice().meet(UsageLattice(S)), UsageLattice())
        self.assertEqual(UsageLattice().meet(UsageLattice(W)), UsageLattice())
        self.assertEqual(UsageLattice().meet(UsageLattice(U)), UsageLattice())

        self.assertEqual(UsageLattice(S).meet(UsageLattice()), UsageLattice())
        self.assertEqual(UsageLattice(S).meet(UsageLattice(W)), UsageLattice())
        self.assertEqual(UsageLattice(S).meet(UsageLattice(U)), UsageLattice(S))

        self.assertEqual(UsageLattice(W).meet(UsageLattice()), UsageLattice())
        self.assertEqual(UsageLattice(W).meet(UsageLattice(S)), UsageLattice())
        self.assertEqual(UsageLattice(W).meet(UsageLattice(U)), UsageLattice(W))

        self.assertEqual(UsageLattice(U).meet(UsageLattice()), UsageLattice())
        self.assertEqual(UsageLattice(U).meet(UsageLattice(S)), UsageLattice(S))
        self.assertEqual(UsageLattice(U).meet(UsageLattice(W)), UsageLattice(W))


if __name__ == '__main__':
    unittest.main()
