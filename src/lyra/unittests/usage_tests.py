"""
Input Data Usage Analysis - Unit Tests
======================================

:Authors: Caterina Urban and Simon Wehrli
"""


import glob
import os
import unittest

from lyra.abstract_domains.usage.usage_domain import SimpleUsageState
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.unittests.runner import TestRunner


class UsageTest(TestRunner):

    def interpreter(self):
        state = SimpleUsageState(self.variables)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3, state)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/usage/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(UsageTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
