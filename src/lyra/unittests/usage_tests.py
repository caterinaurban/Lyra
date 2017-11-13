import glob
import os
import unittest

from lyra.abstract_domains.usage.stack import UsedStack
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.usage.usage_semantics import UsageSemantics
from lyra.unittests.runner import TestRunner


class UsageTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, UsageSemantics(), 3)

    def state(self):
        return UsedStack(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/usage/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(UsageTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
