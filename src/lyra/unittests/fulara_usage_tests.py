"""
Fulara Usage Analysis - Unit Tests
==============================

:Authors: Lowis Engel
"""


import glob
import os
import sys
import unittest
from copy import copy, deepcopy

from lyra.abstract_domains.container.fulara import fulara_domain
from lyra.abstract_domains.container.fulara.fulara_domain import FularaState
from lyra.abstract_domains.container.fulara.interval_wrappers import IntervalSWrapper, \
    IntervalKWrapper, IntervalVWrapper
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.usage.fulara_usage_analysis import FularaUsageAnalysis
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.interval_domain import DictLyraType
from lyra.unittests.runner import TestRunner


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
