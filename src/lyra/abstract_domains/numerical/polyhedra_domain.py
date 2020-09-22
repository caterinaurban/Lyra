"""
Polyhedra Abstract Domain
=========================

Relational abstract domain to be used for **numerical analysis**.
The set of possible numerical values of a program variable in a program state
is represented by a conjunction of linear constraints.

:Authors: Caterina Urban
"""
from typing import Set

from apronpy.polka import PyPolkaMPQstrictManager, PyPolka

from lyra.abstract_domains.numerical.apron_domain import APRONStateWithSummarization
from lyra.abstract_domains.state import State
from lyra.core.expressions import VariableIdentifier


class PolyhedraStateWithSummarization(APRONStateWithSummarization):
    """Polyhedra analysis state based on APRON. An element of the polyhedra abstract domain.

    .. document private methods
    .. automethod:: PolyhedraState._assign
    .. automethod:: PolyhedraState._assume
    .. automethod:: PolyhedraState._output
    .. automethod:: PolyhedraState._substitute

    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        super().__init__(PyPolka, variables, precursory=precursory)

    manager = PyPolkaMPQstrictManager()
