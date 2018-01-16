"""
Assumption Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Madelin Schumacher
"""


import glob
import os
import unittest

from lyra.abstract_domains.quality.assumption_domain import AssumptionState
from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, \
    MultiInputAssumptionLattice
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.unittests.runner import TestRunner


class QualityTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return AssumptionState(self.variables)

    def runTest(self):
        result = self.interpreter().analyze(self.state())
        for node, items in result.result.items():
            if node.identifier == 1:
                items[0] = self.result_to_input_assmps(items[0].stack_top.assmps)
        self.render(result)
        self.check(result)

    def result_to_input_assmps(self, assmps):
        new_assmps = []
        for assmp in assmps:
            if isinstance(assmp, MultiInputAssumptionLattice):
                inner_assmps = self.result_to_input_assmps(assmp.assmps)
                assmp.assmps.clear()
                assmp.assmps.extend(inner_assmps)
                new_assmps.append(assmp)
            else:
                relations = assmp.relations.store[assmp.var_name]
                new_assmps.append((assmp.assmp.type_assumption, relations))
        return new_assmps


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/quality/analysis/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(QualityTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
