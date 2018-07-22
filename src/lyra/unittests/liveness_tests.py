"""
Strongly Live Variable Analysis - Unit Tests
============================================

:Authors: Caterina Urban and Simon Wehrli
"""


import glob
import os
import unittest

import sys

from lyra.abstract_domains.liveness.liveness_domain import StrongLivenessState
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.unittests.runner import TestRunner


class StrongLivenessTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return StrongLivenessState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/liveness/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(StrongLivenessTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite())
    if not result.wasSuccessful():
        sys.exit(1)
