"""
Interval Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Simon Wehrli
"""


import glob
import os
import sys
import unittest

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics
from lyra.unittests.runner import TestRunner


class ForwardIntervalTest(TestRunner):

    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):
        return IntervalState(self.variables)


class BackwardIntervalTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return IntervalState(self.variables)


def forward():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/numerical/interval/forward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('forward/' + os.path.basename(path))
            suite.addTest(ForwardIntervalTest(path))
    return suite


def backward():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/numerical/interval/backward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('backward/' + os.path.basename(path))
            suite.addTest(BackwardIntervalTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result1 = runner.run(forward())
    success1 = result1.wasSuccessful()
    result2 = runner.run(backward())
    success2 = result2.wasSuccessful()
    if not success1 or not success2:
        sys.exit(1)
