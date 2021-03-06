"""
Interval Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Simon Wehrli
"""


import glob
import os
import sys
import unittest

from lyra.abstract_domains.numerical.interval_domain import IntervalStateWithSummarization, \
    IntervalStateWithIndexing
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics
from lyra.unittests.runner import TestRunner


class ForwardIntervalTestWithSummarization(TestRunner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return IntervalStateWithSummarization(self.variables)


class ForwardIntervalTestWithIndexing3(TestRunner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        IntervalStateWithIndexing.bound = 3
        return IntervalStateWithIndexing(self.variables)


class BackwardIntervalTestWithSummarization(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return IntervalStateWithSummarization(self.variables)


class BackwardIntervalTestWithIndexing3(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        IntervalStateWithIndexing.bound = 3
        return IntervalStateWithIndexing(self.variables)


def forward_summarization():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/numerical/interval/forward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('forward/' + os.path.basename(path))
            suite.addTest(ForwardIntervalTestWithSummarization(path))
    name = os.getcwd() + '/numerical/interval/forward/summarization/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('forward/summarization/' + os.path.basename(path))
            suite.addTest(ForwardIntervalTestWithSummarization(path))
    return suite


def forward_indexing3():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/numerical/interval/forward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('forward/' + os.path.basename(path))
            suite.addTest(ForwardIntervalTestWithIndexing3(path))
    name = os.getcwd() + '/numerical/interval/forward/indexing3/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('forward/indexing3/' + os.path.basename(path))
            suite.addTest(ForwardIntervalTestWithIndexing3(path))
    return suite


def backward_summarization():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/numerical/interval/backward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('backward/' + os.path.basename(path))
            suite.addTest(BackwardIntervalTestWithSummarization(path))
    name = os.getcwd() + '/numerical/interval/backward/summarization/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('backward/summarization/' + os.path.basename(path))
            suite.addTest(BackwardIntervalTestWithSummarization(path))
    return suite


def backward_indexing():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/numerical/interval/backward/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('backward/' + os.path.basename(path))
            suite.addTest(BackwardIntervalTestWithIndexing3(path))
    name = os.getcwd() + '/numerical/interval/backward/indexing3/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('backward/indexing3/' + os.path.basename(path))
            suite.addTest(BackwardIntervalTestWithIndexing3(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result1 = runner.run(forward_summarization())
    success1 = result1.wasSuccessful()
    result2 = runner.run(forward_indexing3())
    success2 = result2.wasSuccessful()
    result3 = runner.run(backward_summarization())
    success3 = result3.wasSuccessful()
    result4 = runner.run(backward_indexing())
    success4 = result4.wasSuccessful()
    if not success1 or not success2 or not success3 or not success4:
        sys.exit(1)
