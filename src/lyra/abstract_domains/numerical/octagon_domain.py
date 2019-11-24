"""
Octagon Abstract Domain
=======================

Relational abstract domain to be used for **numerical analysis**.
The set of possible numerical values of a program variable in a program state
is represented by a conjunction of linear constraints.

:Authors: Caterina Urban
"""
from typing import Set

from apronpy.manager import PyManager, PyOctMPQManager
from apronpy.oct import PyOct

from lyra.abstract_domains.numerical.apron_domain import APRONStateWithSummarization
from lyra.abstract_domains.state import State
from lyra.core.expressions import VariableIdentifier


class OctagonStateWithSummarization(APRONStateWithSummarization):
    """Octagon analysis state based on APRON. An element of the octagon abstract domain.

    .. document private methods
    .. automethod:: OctagonState._assign
    .. automethod:: OctagonState._assume
    .. automethod:: OctagonState._output
    .. automethod:: OctagonState._substitute

    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        super().__init__(PyOct, variables, precursory=precursory)

    manager: PyManager = PyOctMPQManager()
