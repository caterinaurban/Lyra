import unittest

from math import inf
from lyra.abstract_domains.numerical.interval_domain import IntervalLattice


class TestIntervalLattice(unittest.TestCase):

    def test_init(self):
        self.assertFalse(IntervalLattice().is_bottom())
        self.assertTrue(IntervalLattice().is_top())

        self.assertFalse(IntervalLattice(0, 1).is_bottom())
        self.assertFalse(IntervalLattice(0, 1).is_top())

        self.assertEqual(IntervalLattice(upper=2), IntervalLattice(-inf, 2))
        self.assertEqual(IntervalLattice(lower=3), IntervalLattice(3, inf))

        self.assertTrue(IntervalLattice(1, 0).is_bottom())
        self.assertFalse(IntervalLattice(1, 0).is_top())

    def test_leq(self):
        self.assertFalse(IntervalLattice().less_equal(IntervalLattice(0, 1)))
        self.assertFalse(IntervalLattice().less_equal(IntervalLattice(1, 0)))

        self.assertTrue(IntervalLattice(0, 1).less_equal(IntervalLattice()))
        self.assertFalse(IntervalLattice(0, 1).less_equal(IntervalLattice(1, 0)))

        self.assertTrue(IntervalLattice(1, 0).less_equal(IntervalLattice()))
        self.assertTrue(IntervalLattice(1, 0).less_equal(IntervalLattice(0, 1)))

    def test_join(self):
        self.assertEqual(IntervalLattice().join(IntervalLattice(0, 1)), IntervalLattice())
        self.assertEqual(IntervalLattice().join(IntervalLattice(1, 0)), IntervalLattice())

        self.assertEqual(IntervalLattice(0, 1).join(IntervalLattice()), IntervalLattice())
        self.assertEqual(IntervalLattice(0, 1).join(IntervalLattice(1, 0)), IntervalLattice(0, 1))

        self.assertEqual(IntervalLattice(1, 0).join(IntervalLattice()), IntervalLattice())
        self.assertEqual(IntervalLattice(1, 0).join(IntervalLattice(0, 1)), IntervalLattice(0, 1))

        self.assertEqual(IntervalLattice(upper=3).join(IntervalLattice(lower=2)), IntervalLattice())
        self.assertEqual(IntervalLattice(2, 4).join(IntervalLattice(1, 3)), IntervalLattice(1, 4))
        self.assertEqual(IntervalLattice(1, 2).join(IntervalLattice(3, 4)), IntervalLattice(1, 4))

    def test_meet(self):
        self.assertEqual(IntervalLattice().meet(IntervalLattice(0, 1)), IntervalLattice(0, 1))
        self.assertEqual(IntervalLattice().meet(IntervalLattice(1, 0)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(0, 1).meet(IntervalLattice()), IntervalLattice(0, 1))
        self.assertEqual(IntervalLattice(0, 1).meet(IntervalLattice(1, 0)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(1, 0).meet(IntervalLattice()), IntervalLattice(1, 0))
        self.assertEqual(IntervalLattice(1, 0).meet(IntervalLattice(0, 1)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(upper=3).meet(IntervalLattice(lower=2)), IntervalLattice(2, 3))
        self.assertEqual(IntervalLattice(2, 4).meet(IntervalLattice(1, 3)), IntervalLattice(2, 3))
        self.assertEqual(IntervalLattice(1, 2).meet(IntervalLattice(3, 4)), IntervalLattice(1, 0))

    def test_widening(self):
        self.assertEqual(IntervalLattice().widening(IntervalLattice(0, 1)), IntervalLattice())
        self.assertEqual(IntervalLattice().widening(IntervalLattice(1, 0)), IntervalLattice())

        self.assertEqual(IntervalLattice(0, 1).widening(IntervalLattice()), IntervalLattice())
        self.assertEqual(IntervalLattice(0, 1).widening(IntervalLattice(1, 0)), IntervalLattice(0, 1))

        self.assertEqual(IntervalLattice(1, 0).widening(IntervalLattice()), IntervalLattice())
        self.assertEqual(IntervalLattice(1, 0).widening(IntervalLattice(0, 1)), IntervalLattice(0, 1))

        self.assertEqual(IntervalLattice(upper=3).widening(IntervalLattice(lower=2)), IntervalLattice())
        self.assertEqual(IntervalLattice(2, 4).widening(IntervalLattice(1, 3)), IntervalLattice(upper=4))
        self.assertEqual(IntervalLattice(1, 2).widening(IntervalLattice(3, 4)), IntervalLattice(lower=1))

    def test_neg(self):
        self.assertEqual(IntervalLattice().neg(), IntervalLattice())

        self.assertEqual(IntervalLattice(0, 1).neg(), IntervalLattice(-1, 0))

        self.assertEqual(IntervalLattice(upper=2).neg(), IntervalLattice(-2, inf))
        self.assertEqual(IntervalLattice(lower=3).neg(), IntervalLattice(-inf, -3))

        self.assertEqual(IntervalLattice(1, 0).neg(), IntervalLattice(1, 0))

    def test_add(self):
        self.assertEqual(IntervalLattice().add(IntervalLattice(0, 1)), IntervalLattice())
        self.assertEqual(IntervalLattice().add(IntervalLattice(1, 0)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(0, 1).add(IntervalLattice()), IntervalLattice())
        self.assertEqual(IntervalLattice(0, 1).add(IntervalLattice(1, 0)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(1, 0).add(IntervalLattice()), IntervalLattice(1, 0))
        self.assertEqual(IntervalLattice(1, 0).add(IntervalLattice(0, 1)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(upper=3).add(IntervalLattice(lower=2)), IntervalLattice())
        self.assertEqual(IntervalLattice(2, 4).add(IntervalLattice(1, 3)), IntervalLattice(3, 7))
        self.assertEqual(IntervalLattice(1, 2).add(IntervalLattice(3, 4)), IntervalLattice(4, 6))

    def test_sub(self):
        self.assertEqual(IntervalLattice().sub(IntervalLattice(0, 1)), IntervalLattice())
        self.assertEqual(IntervalLattice().sub(IntervalLattice(1, 0)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(0, 1).sub(IntervalLattice()), IntervalLattice())
        self.assertEqual(IntervalLattice(0, 1).sub(IntervalLattice(1, 0)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(1, 0).sub(IntervalLattice()), IntervalLattice(1, 0))
        self.assertEqual(IntervalLattice(1, 0).sub(IntervalLattice(0, 1)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(upper=3).sub(IntervalLattice(lower=2)), IntervalLattice(-inf, 1))
        self.assertEqual(IntervalLattice(2, 4).sub(IntervalLattice(1, 3)), IntervalLattice(-1, 3))
        self.assertEqual(IntervalLattice(1, 2).sub(IntervalLattice(3, 4)), IntervalLattice(-3, -1))

    def test_mult(self):
        self.assertEqual(IntervalLattice().mult(IntervalLattice(0, 1)), IntervalLattice())
        self.assertEqual(IntervalLattice().mult(IntervalLattice(1, 0)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(0, 1).mult(IntervalLattice()), IntervalLattice())
        self.assertEqual(IntervalLattice(0, 1).mult(IntervalLattice(1, 0)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(1, 0).mult(IntervalLattice()), IntervalLattice(1, 0))
        self.assertEqual(IntervalLattice(1, 0).mult(IntervalLattice(0, 1)), IntervalLattice(1, 0))

        self.assertEqual(IntervalLattice(upper=3).mult(IntervalLattice(lower=2)), IntervalLattice())
        self.assertEqual(IntervalLattice(2, 4).mult(IntervalLattice(1, 3)), IntervalLattice(2, 12))
        self.assertEqual(IntervalLattice(1, 2).mult(IntervalLattice(3, 4)), IntervalLattice(3, 8))

if __name__ == '__main__':
    unittest.main()
