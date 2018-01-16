"""
Assumption Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Madelin Schumacher
"""


import glob
import os
import unittest

import time

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
        start = time.time()
        result = self.interpreter().analyze(self.state())
        analysis = round((time.time()-start) * 10000)
        sub_time1 = 0
        assume_time = 0
        for states in result.result.values():
            for state in states:
                sub_time1 += state.substitute_time
                assume_time += state.assume_time
        print(f"substitute_time:{sub_time1}")
        print(f"assume_time:{assume_time}")
        print(f"analysis else:{analysis-sub_time1-assume_time}")
        print(f"-----analysis:{analysis}")
        print("")
        for node, items in result.result.items():
            if node.identifier == 1:
                items[0] = self.result_to_input_assmps(items[0].stack_top.assmps)
        self.render(result)
        self.check(result)

    def result_to_input_assmps(self, assmps):
        new_assmps = []
        for assmp in assmps:
            #if isinstance(assmp, AssumptionLattice):
            if isinstance(assmp, MultiInputAssumptionLattice):
                inner_assmps = self.result_to_input_assmps(assmp.assmps)
                assmp.assmps = inner_assmps
                new_assmps.append(assmp)
            else:
                relations = assmp.relations.store[assmp.var_name]
                new_assmps.append((assmp.assmp.type_assumption, relations))
            #else:
            #    assmp._assmps = self.result_to_input_assmps(assmp.assmps)
            #    new_assmps.append(assmp)
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
