"""
Input Data Usage Analysis - Unit Tests
======================================

:Authors: Caterina Urban and Simon Wehrli and Lowis Engel
"""


import glob
import os
import unittest

import sys

from lyra.abstract_domains.usage.usage_domain import SimpleUsageState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.usage.fulara_usage_analysis import FularaUsageAnalysis
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.unittests.runner import TestRunner


class UsageTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return SimpleUsageState(self.variables)


class FularaUsageTest(TestRunner):

    def interpreter(self):
        analysis = FularaUsageAnalysis()
        analysis._cfg = self.cfg
        return analysis.interpreter()

    def state(self):  # initial state
        analysis = FularaUsageAnalysis()
        analysis._cfg = self.cfg
        return analysis.state()


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/usage/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(UsageTest(path))
    name = os.getcwd() + '/usage/fulara/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(FularaUsageTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite())
    if not result.wasSuccessful():
        sys.exit(1)
