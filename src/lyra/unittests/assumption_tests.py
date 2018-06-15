"""
Assumption Analysis - Unit Tests
================================

:Authors: Caterina Urban and Madelin Schumacher
"""
import glob
import os
import unittest

from lyra.abstract_domains.assumption.type_domain import TypeState
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.unittests.runner import TestRunner


class TypeTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/assumption/type/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(TypeTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
