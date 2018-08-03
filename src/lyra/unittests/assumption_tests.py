"""
Assumption Analysis - Unit Tests
================================

:Authors: Caterina Urban and Radwa Sherif Abdelbar and Madelin Schumacher
"""
import glob
import os
import unittest

import sys

from lyra.abstract_domains.assumption.alphabet_domain import AlphabetState
from lyra.abstract_domains.assumption.assumption_domain import TypeRangeAssumptionState, \
    TypeAlphabetAssumptionState, TypeRangeAlphabetAssumptionState, TypeQuantityAssumptionState
from lyra.abstract_domains.assumption.quantity_domain import QuantityState
from lyra.abstract_domains.assumption.range_domain import RangeState
from lyra.abstract_domains.assumption.type_domain import TypeState
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.unittests.runner import TestRunner


class TypeTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeState(self.variables)


class QuantityTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return QuantityState(self.variables)


class RangeTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return RangeState(self.variables)


class AlphabetTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return AlphabetState(self.variables)


class TypeQuantityAssumptionTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeQuantityAssumptionState(self.variables)


class TypeRangeAssumptionTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAssumptionState(self.variables)


class TypeAlphabetAssumptionTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeAlphabetAssumptionState(self.variables)


class TypeRangeAlphabetAssumptionTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAlphabetAssumptionState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/assumption/type/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(TypeTest(path))
    name = os.getcwd() + '/assumption/quantity/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(QuantityTest(path))
    name = os.getcwd() + '/assumption/range/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(RangeTest(path))
    name = os.getcwd() + '/assumption/alphabet/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(AlphabetTest(path))
    name = os.getcwd() + '/assumption/type+quantity/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(TypeQuantityAssumptionTest(path))
    name = os.getcwd() + '/assumption/type+range/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(TypeRangeAssumptionTest(path))
    name = os.getcwd() + '/assumption/type+string/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(TypeAlphabetAssumptionTest(path))
    name = os.getcwd() + '/assumption/type+range+alphabet/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(TypeRangeAlphabetAssumptionTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite())
    if not result.wasSuccessful():
        sys.exit(1)
