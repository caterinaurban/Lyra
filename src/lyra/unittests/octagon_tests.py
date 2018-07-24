import glob
import os
import unittest

from lyra.abstract_domains.assumption.character_domain import CharacterState
from lyra.abstract_domains.assumption.octagons_domain import OctagonState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.unittests.runner import TestRunner


class BackwardOctagonTest(TestRunner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return OctagonState(self.variables)


def test_suite():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/octagon/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(BackwardOctagonTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())
