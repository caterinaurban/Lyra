import glob
import os
import unittest

from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.unittests.runner import TestRunner


class IntervalBackwardsTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return IntervalState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/interval_backwards/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(IntervalBackwardsTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())