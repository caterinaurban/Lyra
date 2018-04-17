"""
Sign Analysis - Unit Tests
==========================

:Author: Jérôme Dohrau
"""

import glob
import os
import unittest

from lyra.abstract_domains.numerical.sign_domain import SignState
from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.forward import DefaultForwardSemantics
from lyra.unittests.runner import TestRunner


class SignTest(TestRunner):

    def interpreter(self):
        return ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)

    def state(self):
        return SignState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + "/sign/**.py"
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(SignTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
