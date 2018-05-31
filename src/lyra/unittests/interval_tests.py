"""
Interval Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Simon Wehrli
"""


import glob
import os
import unittest

from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.unittests.runner import TestRunner


class ForwardIntervalTest(TestRunner):

    def interpreter(self):
        state = IntervalState(self.variables)
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3, state)


class BackwardIntervalTest(TestRunner):

    def interpreter(self):
        state = IntervalState(self.variables)
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3, state)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/interval/forward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(ForwardIntervalTest(path))
    name = os.getcwd() + '/interval/backward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(BackwardIntervalTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
