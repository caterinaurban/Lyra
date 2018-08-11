"""
Type Lattice - Unit Tests
=========================

:Author: Caterina Urban
"""
import unittest
from typing import List

from lyra.abstract_domains.assumption.type_domain import TypeLattice
from lyra.unittests.abstract_tests import AbstractTest


class TestTypeLattice(AbstractTest.LatticeTest):

    def default(self):
        return TypeLattice()

    @staticmethod
    def boolean() -> TypeLattice:
        return TypeLattice(TypeLattice.Status.Boolean)

    @staticmethod
    def integer() -> TypeLattice:
        return TypeLattice(TypeLattice.Status.Integer)

    @staticmethod
    def float() -> TypeLattice:
        return TypeLattice(TypeLattice.Status.Float)

    @staticmethod
    def string() -> TypeLattice:
        return TypeLattice(TypeLattice.Status.String)

    def elements(self) -> List[TypeLattice]:
        return [self.bottom(), self.boolean(), self.integer(), self.string(), self.top()]

    def test_less_equal(self):
        super().test_less_equal()
        self.assertTrue(self.boolean().less_equal(self.integer()))
        self.assertTrue(self.integer().less_equal(self.float()))
        self.assertTrue(self.float().less_equal(self.string()))
        self.assertFalse(self.string().less_equal(self.float()))
        self.assertFalse(self.float().less_equal(self.integer()))
        self.assertFalse(self.integer().less_equal(self.boolean()))

    def test_join(self):
        super().test_join()
        self.assertEqual(self.boolean().join(self.integer()), self.integer())
        self.assertEqual(self.integer().join(self.float()), self.float())
        self.assertEqual(self.float().join(self.string()), self.string())

    def test_meet(self):
        super().test_meet()
        self.assertEqual(self.boolean().meet(self.integer()), self.boolean())
        self.assertEqual(self.integer().meet(self.float()), self.integer())
        self.assertEqual(self.float().meet(self.string()), self.float())

    def test_neg(self):
        self.assertEqual(self.boolean().neg(), self.integer())
        self.assertEqual(self.integer().neg(), self.integer())
        self.assertEqual(self.float().neg(), self.float())
        self.assertEqual(self.string().neg(), self.bottom())

    def test_add(self):
        self.assertEqual(self.boolean().add(self.boolean()), self.integer())
        self.assertEqual(self.boolean().add(self.integer()), self.integer())
        self.assertEqual(self.boolean().add(self.float()), self.float())
        self.assertEqual(self.boolean().add(self.string()), self.bottom())
        self.assertEqual(self.integer().add(self.boolean()), self.integer())
        self.assertEqual(self.integer().add(self.integer()), self.integer())
        self.assertEqual(self.integer().add(self.float()), self.float())
        self.assertEqual(self.integer().add(self.string()), self.bottom())
        self.assertEqual(self.float().add(self.boolean()), self.float())
        self.assertEqual(self.float().add(self.integer()), self.float())
        self.assertEqual(self.float().add(self.float()), self.float())
        self.assertEqual(self.float().add(self.string()), self.bottom())
        self.assertEqual(self.string().add(self.boolean()), self.bottom())
        self.assertEqual(self.string().add(self.integer()), self.bottom())
        self.assertEqual(self.string().add(self.float()), self.bottom())
        self.assertEqual(self.string().add(self.string()), self.string())

    def test_sub(self):
        self.assertEqual(self.boolean().sub(self.boolean()), self.integer())
        self.assertEqual(self.boolean().sub(self.integer()), self.integer())
        self.assertEqual(self.boolean().sub(self.float()), self.float())
        self.assertEqual(self.boolean().sub(self.string()), self.bottom())
        self.assertEqual(self.integer().sub(self.boolean()), self.integer())
        self.assertEqual(self.integer().sub(self.integer()), self.integer())
        self.assertEqual(self.integer().sub(self.float()), self.float())
        self.assertEqual(self.integer().sub(self.string()), self.bottom())
        self.assertEqual(self.float().sub(self.boolean()), self.float())
        self.assertEqual(self.float().sub(self.integer()), self.float())
        self.assertEqual(self.float().sub(self.float()), self.float())
        self.assertEqual(self.float().sub(self.string()), self.bottom())
        self.assertEqual(self.string().sub(self.boolean()), self.bottom())
        self.assertEqual(self.string().sub(self.integer()), self.bottom())
        self.assertEqual(self.string().sub(self.float()), self.bottom())
        self.assertEqual(self.string().sub(self.string()), self.bottom())

    def test_mult(self):
        self.assertEqual(self.boolean().mult(self.boolean()), self.integer())
        self.assertEqual(self.boolean().mult(self.integer()), self.integer())
        self.assertEqual(self.boolean().mult(self.float()), self.float())
        self.assertEqual(self.boolean().mult(self.string()), self.string())
        self.assertEqual(self.integer().mult(self.boolean()), self.integer())
        self.assertEqual(self.integer().mult(self.integer()), self.integer())
        self.assertEqual(self.integer().mult(self.float()), self.float())
        self.assertEqual(self.integer().mult(self.string()), self.string())
        self.assertEqual(self.float().mult(self.boolean()), self.float())
        self.assertEqual(self.float().mult(self.integer()), self.float())
        self.assertEqual(self.float().mult(self.float()), self.float())
        self.assertEqual(self.float().mult(self.string()), self.bottom())
        self.assertEqual(self.string().mult(self.boolean()), self.string())
        self.assertEqual(self.string().mult(self.integer()), self.string())
        self.assertEqual(self.string().mult(self.float()), self.bottom())
        self.assertEqual(self.string().mult(self.string()), self.bottom())

    def test_div(self):
        self.assertEqual(self.boolean().div(self.boolean()), self.float())
        self.assertEqual(self.boolean().div(self.integer()), self.float())
        self.assertEqual(self.boolean().div(self.float()), self.float())
        self.assertEqual(self.boolean().div(self.string()), self.bottom())
        self.assertEqual(self.integer().div(self.boolean()), self.float())
        self.assertEqual(self.integer().div(self.integer()), self.float())
        self.assertEqual(self.integer().div(self.float()), self.float())
        self.assertEqual(self.integer().div(self.string()), self.bottom())
        self.assertEqual(self.float().div(self.boolean()), self.float())
        self.assertEqual(self.float().div(self.integer()), self.float())
        self.assertEqual(self.float().div(self.float()), self.float())
        self.assertEqual(self.float().div(self.string()), self.bottom())
        self.assertEqual(self.string().div(self.boolean()), self.bottom())
        self.assertEqual(self.string().div(self.integer()), self.bottom())
        self.assertEqual(self.string().div(self.float()), self.bottom())
        self.assertEqual(self.string().div(self.string()), self.bottom())


if __name__ == '__main__':
    unittest.main()
