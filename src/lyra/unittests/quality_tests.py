"""
Assumption Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Madelin Schumacher
"""


import glob
import os
import unittest
from typing import List

from lyra.abstract_domains.quality.assumption_domain import AssumptionState
from lyra.core.expressions import Identifier, LengthIdentifier
from lyra.core.types import ListLyraType, StringLyraType
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.unittests.runner import TestRunner


class QualityTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return AssumptionState(self.variables)

    @property
    def variables(self) -> List[Identifier]:
        all_vars = super().variables
        for var in all_vars:
            if isinstance(var.typ, (ListLyraType, StringLyraType)):
                all_vars.append(LengthIdentifier(var))
        return all_vars

    def runTest(self):
        result = self.interpreter().analyze(self.state())
        for node, items in result.result.items():
            if node.identifier == 1:
                items[0] = items[0].stack_top.assmps
        self.render(result)
        self.check(result)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/quality/analysis/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(QualityTest(path))
    name = os.getcwd() + '/quality/analysis/relationships/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(QualityTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
