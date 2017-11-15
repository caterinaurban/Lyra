"""
Syntactic Usage Abstract Domain
===============================

Abstract domain to be used for **input data usage analysis** using syntactic variable dependencies.
A program variable can have value *U* (used), *S* (scoped), *W* (written), and *N* (not used).

:Authors: Simon Wehrli and Caterina Urban
"""

from enum import Flag

from lyra.abstract_domains.lattice import Lattice
from lyra.core.utils import copy_docstring


class UsageLattice(Lattice):
    """Usage lattice::

            U
          /   \\
        S       O
          \\   /
            N

    The default lattice element is ``N`` (not used).

    .. document private methods
    .. automethod:: UsageLattice._less_equal
    .. automethod:: UsageLattice._meet
    .. automethod:: UsageLattice._join
    .. automethod:: UsageLattice._widening
    """
    class Status(Flag):
        """Usage status.

        The current lattice element can be:

        * ``U`` (used): used at the current nesting level

        * ``S`` (scoped): used at a lower nesting level

        * ``W`` (written): used at a lower nesting level and modified at the current nesting level

        * ``N`` (not used): unused
        """
        U = 3
        S = 2
        W = 1
        N = 0

    def __init__(self, usage: Status = Status.N):
        super().__init__()
        self._element = usage

    @property
    def element(self):
        """Current lattice element."""
        return self._element

    def __repr__(self):
        return self.element.name

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        """The bottom lattice element is ``N`` (not used)."""
        self.replace(UsageLattice(UsageLattice.Status.N))
        return self

    @copy_docstring(Lattice.top)
    def top(self):
        """The top lattice element is ``U`` (used)."""
        self.replace(UsageLattice(UsageLattice.Status.U))
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self):
        return self.element == UsageLattice.Status.N

    @copy_docstring(Lattice.is_top)
    def is_top(self):
        return self.element == UsageLattice.Status.U

    @copy_docstring(Lattice.less_equal)
    def _less_equal(self, other: 'UsageLattice') -> bool:
        return self.element == other.element

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'UsageLattice') -> 'UsageLattice':
        self.replace(UsageLattice(self.element & other.element))
        return self

    @copy_docstring(Lattice._join)
    def _join(self, other: 'UsageLattice') -> 'UsageLattice':
        self.replace(UsageLattice(self.element | other.element))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'UsageLattice') -> 'UsageLattice':
        return self._join(other)
