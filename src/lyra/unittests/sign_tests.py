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
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return SignState(self.variables)


class BackwardSignTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return SignState(self.variables)


def forward():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/numerical/sign/forward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('forward/' + os.path.basename(path))
            suite.addTest(ForwardSignTest(path))
    return suite


def backward():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/numerical/sign/backward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('backward/' + os.path.basename(path))
            suite.addTest(BackwardSignTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result1 = runner.run(forward())
    success1 = result1.wasSuccessful()
    result2 = runner.run(backward())
    success2 = result2.wasSuccessful()
    if not success1 or not success2:
        sys.exit(1)
