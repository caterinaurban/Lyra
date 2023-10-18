"""
Data Usage Analysis Dataframes - Unit Tests
======================================

:Authors: Caterina Urban and Kevin Pinochet
"""


import glob
import os
import unittest

import sys

from lyra.abstract_domains.usage.dataframe_usage_domain import DataFrameColumnUsageState
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.dataframe_usage_semantics import DataFrameColumnUsageSemantics
from lyra.unittests.runner import TestRunner


class UsageTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DataFrameColumnUsageSemantics(), 3)

    def state(self):
        return DataFrameColumnUsageState(self.variables)

def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/usage/dataframes/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            print(os.path.basename(path))
            suite.addTest(UsageTest(path))
    # name = os.getcwd() + '/usage/fulara/**.py'
    # for path in glob.iglob(name):
    #     if os.path.basename(path) != "__init__.py":
    #         print('fulara/' + os.path.basename(path))
    #         suite.addTest(FularaIntervalUsageTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite())
    if not result.wasSuccessful():
        sys.exit(1)
