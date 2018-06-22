"""
Assumption Abstract Domain
==========================

Abstract domain to be used for **input data assumption analysis**.

:Authors: Caterina Urban and Radwa Sherif Abdelbar
"""
from abc import ABCMeta
from collections import defaultdict
from typing import List, Dict
from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.state import State
from lyra.core.expressions import VariableIdentifier, Expression
from lyra.core.statements import ProgramPoint


class InputMixin(State, metaclass=ABCMeta):
    """Mixin to add a mechanism for recording and retrieving assumptions on the input data.

    Assumptions are recorded in the class member ``inputs``, which is a map
    from each program point to the list of assumptions on the input data read at that point.
    """
    inputs: Dict[ProgramPoint, List[Lattice]]

    def __init__(self):
        super().__init__()
        type(self).inputs = defaultdict(list)

    def record(self, assumption: Lattice):
        """Record an assumption.

        :param assumption: assumption to be recorded
        :return: current state modified to record the assumption
        """
        type(self).inputs[self.pp].append(assumption)

    def retrieve(self, pp: ProgramPoint):
        """Retrieve the assumptions corresponding to a given program point.

        :param pp: program point of interest
        :return: the list of assumptions corresponding to the given program point
        """
        return type(self).inputs[pp]
