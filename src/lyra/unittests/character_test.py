"""
Interval Analysis - Unit Tests
==============================

:Authors: Caterina Urban and Simon Wehrli
"""


import glob
import os
import unittest

from lyra.abstract_domains.string.character_domain import CharacterState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.unittests.runner import TestRunner


class BackwardCharacterTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return CharacterState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/character/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(BackwardCharacterTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
