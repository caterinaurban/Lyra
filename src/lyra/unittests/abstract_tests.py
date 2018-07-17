"""
Abstract Unit Tests
===================

:Author: Jérôme Dohrau and Caterina Urban
"""
import unittest
from abc import abstractmethod, ABCMeta
from copy import deepcopy
from typing import List
from lyra.abstract_domains.lattice import Lattice, ArithmeticMixin


class AbstractTest:

    class LatticeTest(unittest.TestCase, metaclass=ABCMeta):
        """A class that provides generic test cases for lattices."""

        @abstractmethod
        def default(self) -> Lattice:
            """ Default lattice element."""

        def bottom(self):
            """ Bottom lattice element."""
            return self.default().bottom()

        def top(self):
            """Top lattice element."""
            return self.default().top()

        @abstractmethod
        def elements(self) -> List[Lattice]:
            """List of lattice elements."""

        def test_bottom(self):
            # bottom element is bottom
            self.assertTrue(self.bottom().is_bottom())
            # all other elements are not
            for element in self.elements():
                if element != self.bottom():
                    self.assertFalse(element.is_bottom())

        def test_top(self):
            # top element is top
            self.assertTrue(self.top().is_top())
            # all other elements are not
            for element in self.elements():
                if element != self.top():
                    self.assertFalse(element.is_top())

        def test_equivalence(self):
            # equivalent elements are equal
            for left in self.elements():
                for right in self.elements():
                    if left.less_equal(right) and right.less_equal(left):
                        self.assertEqual(left, right)

        def test_less_equal(self):
            # top is largest element
            for element in self.elements():
                self.assertTrue(element.less_equal(self.top()))
            # bottom is smallest element
            for element in self.elements():
                self.assertTrue(self.bottom().less_equal(element))

        def test_join(self):
            # join is commutative
            for left in self.elements():
                for right in self.elements():
                    self.assertEqual(deepcopy(left).join(right), right.join(left))
            # check precision
            for left in self.elements():
                for right in self.elements():
                    if left.less_equal(right):
                        self.assertEqual(left.join(right), right)

        def test_meet(self):
            # meet is commutative
            for left in self.elements():
                for right in self.elements():
                    self.assertEqual(deepcopy(left).meet(right), right.meet(left))
            # check precision
            for left in self.elements():
                for right in self.elements():
                    if left.less_equal(right):
                        self.assertEqual(right.meet(left), left)

        def test_widening(self):
            # widening over-approximates join
            for left in self.elements():
                for right in self.elements():
                    self.assertTrue((deepcopy(left).join(right)).less_equal(left.widening(right)))
            # check precision
            for left in self.elements():
                for right in self.elements():
                    if left.less_equal(right):
                        self.assertEqual(left.widening(right), right)

    class ArithmeticLatticeTest(LatticeTest):
        """A class that provides generic test cases for lattices with arithmetic operations."""

        @abstractmethod
        def default(self) -> ArithmeticMixin:
            """ Default lattice element."""

        @abstractmethod
        def elements(self) -> List[ArithmeticMixin]:
            """List of lattice elements."""

        def test_neg(self):
            self.assertEqual(self.bottom().neg(), self.bottom())
            self.assertEqual(self.top().neg(), self.top())

        def test_add(self):
            # add is commutative
            for left in self.elements():
                for right in self.elements():
                    self.assertEqual(deepcopy(left).add(right), deepcopy(right).add(left))

        def test_sub(self):
            pass

        def test_mult(self):
            # mult is commutative
            for left in self.elements():
                for right in self.elements():
                    self.assertEqual(deepcopy(left).mult(right), deepcopy(right).mult(left))
