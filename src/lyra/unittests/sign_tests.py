"""
Sign Analysis - Unit Tests
==========================

:Author: Jérôme Dohrau and Caterina Urban
"""

import glob
import os
import unittest

import sys

from lyra.abstract_domains.numerical.sign_domain import SignState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics
from lyra.unittests.runner import TestRunner


class ForwardSignTest(TestRunner):

    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):
        return SignState(self.variables)


class BackwardSignTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return SignState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + "/numerical/sign/forward/**.py"
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(ForwardSignTest(path))
    name = os.getcwd() + '/numerical/sign/backward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(BackwardSignTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite())
    if not result.wasSuccessful():
        sys.exit(1)
