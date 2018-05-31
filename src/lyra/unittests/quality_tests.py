"""
Assumption Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Madelin Schumacher
"""


import glob
import os
import unittest

from lyra.abstract_domains.quality.assumption_domain import AssumptionState
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.unittests.runner import TestRunner


class QualityTest(TestRunner):

    def interpreter(self):
        state = AssumptionState(self.variables)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3, state)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/quality/analysis/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(QualityTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
