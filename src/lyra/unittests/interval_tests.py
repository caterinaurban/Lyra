"""
Interval Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Simon Wehrli
"""


import glob
import os
import unittest

from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.unittests.runner import TestRunner


class IntervalTest(TestRunner):

    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):
        return IntervalState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/interval/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(IntervalTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
