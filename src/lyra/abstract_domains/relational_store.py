"""
Relational Store
=====

Abstract representation of a abstract state handling multiple variables and POSSIBLY their relations

:Authors: Lowis Engel
"""
from abc import ABCMeta
from typing import List

from lyra.core.expressions import VariableIdentifier
from lyra.abstract_domains.lattice import Lattice


class RelationalStore(Lattice, metaclass=ABCMeta):
    """Mutable element of a relational store, abstracting multiple variables

    .. warning::
        Lattice operations modify the current store.

    .. document private methods
    .. automethod:: Store._less_equal
    .. automethod:: Store._meet
    .. automethod:: Store._join
    """
    def __init__(self, variables: List[VariableIdentifier]):
        """

        :param variables: list of program variables to handle
        """
        super().__init__()
        self._variables = variables

    @property
    def variables(self):
        """Variables of the current store."""
        return self._variables