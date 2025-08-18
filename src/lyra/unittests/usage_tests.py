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
from lyra.abstract_domains.usage.dataframe_usage_domain import DataFrameColumnUsageState
from lyra.engine.backward import BackwardInterpreter
# from lyra.engine.usage.fulara_usage_analysis import FularaIntervalUsageAnalysis
from lyra.engine.usage.dataframe_usage_analysis import DataFrameColumnUsageAnalysis
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.dataframe_usage_semantics import DataFrameColumnUsageSemantics
from lyra.unittests.runner import TestRunner


class UsageTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return SimpleUsageState(self.variables)


class FularaIntervalUsageTest(TestRunner):

    def interpreter(self):
        analysis = FularaIntervalUsageAnalysis()
        analysis._cfgs = self.cfgs
        return analysis.interpreter()

    def state(self):  # initial state
        analysis = FularaIntervalUsageAnalysis()
        analysis._cfgs = self.cfgs
        return analysis.state()

class DataFrameColumnUsageTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DataFrameColumnUsageSemantics(), 3)

    def state(self):
        return DataFrameColumnUsageState(self.variables)

def test_suite():
    suite = unittest.TestSuite()
    # name = os.getcwd() + '/usage/**.py'
    # for path in glob.iglob(name):
    #     if os.path.basename(path) != "__init__.py":
    #         print(os.path.basename(path))
    #         suite.addTest(UsageTest(path))

    # name = os.getcwd() + '/usage/fulara/**.py'
    # for path in glob.iglob(name):
    #     if os.path.basename(path) != "__init__.py":
    #         print('fulara/' + os.path.basename(path))
    #         suite.addTest(FularaIntervalUsageTest(path))

    name = os.getcwd() + '/usage/dataframes/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print('dataframes/' + os.path.basename(path))
            suite.addTest(DataFrameColumnUsageTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite())
    if not result.wasSuccessful():
        sys.exit(1)
