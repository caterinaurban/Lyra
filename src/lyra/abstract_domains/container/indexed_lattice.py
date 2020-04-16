"""
Indexed Lattice
===============

The elements of the lattice are a bounded number of indexed lattice elements.

:Author: Caterina Urban
"""
from copy import deepcopy
from typing import Dict, List, Set, Type

from lyra.abstract_domains.lattice import SequenceMixin, BottomMixin, Lattice
from lyra.core.expressions import Literal
from lyra.core.utils import copy_docstring


class IndexedLattice(BottomMixin, SequenceMixin):
    """Indexed lattice.

    The default abstraction is the top element ``_ -> L.top()``.

    .. document private methods
    .. automethod:: IndexedLattice._less_equal
    .. automethod:: IndexedLattice._meet
    .. automethod:: IndexedLattice._join
    .. automethod:: IndexedLattice._widening
    .. automethod:: IndexedLattice._concat
    """

    def __init__(self, lattice: Type[Lattice], indexed: Dict[str, Lattice] = None, bound: int = 3):
        super().__init__()
        self._lattice: Type[Lattice] = lattice
        self._indexed = {'_': self._lattice()}
        if indexed is not None:
            keys: List[str] = sorted(indexed.keys())
            for i in range(min(bound, len(keys))):
                self._indexed[keys[i]] = indexed[keys[i]]
            rest = self._lattice().bottom()
            for j in range(bound, len(keys)):
                rest = rest.join(indexed[keys[j]])
            if '_' in indexed:
                self._indexed['_'] = self._indexed['_'].join(rest)
            else:
                self._indexed['_'] = rest
        self._bound = bound

    @property
    def lattice(self):
        """Current indexed (sub)lattice.

        :return: the (sub)lattice whose elements are currently indexed
        """
        return self._lattice

    @property
    def indexed(self):
        """Current indexed (sub)lattice elements.

        :return: the current indexed (sub)lattice elements
        """
        return self._indexed

    @property
    def indexes(self):
        """Current indexes.

        :return: the current indexes (sorted)
        """
        items = sorted(self.indexed.keys())
        if self.default.is_bottom():
            return items[:-1]   # exclude the (unused) default index
        return items

    @property
    def size(self):
        """Current number of indexed (sub)lattice elements.

        :return: the current number of indexed (sub)lattice elements
        """
        return len(self.indexed) - 1

    @property
    def bound(self):
        """Current bound on the indexed (sub)lattice elements.

        :return: the current bound on the indexed (sub)lattice elements
        """
        return self._bound

    @property
    def default(self):
        """Default indexed (sub)lattice elements.

        :return: the current default indexed (sub)lattice element
        """
        return self.indexed['_']

    def summarize(self) -> 'Lattice':
        """Summarize the indexed (sub)lattice elements into a single (sub)lattice element.

        :return: the (sub)lattice element representing the summary of the indexed elements
        """
        summary: Lattice = self.lattice().bottom()
        for itv in self.indexed.values():
            summary = summary.join(deepcopy(itv))
        return summary

    def set_subscript(self, idx: str, itv: Lattice) -> 'IndexedLattice':
        """Set a specific index to a new (sub)lattice element.

        :param idx: the index to be set
        :param itv: the new (sub)lattice element
        :return: current lattice element modified to index the new (sub)lattice element
        """
        if idx in self.indexed or self.size < self.bound:
            self.indexed[idx] = itv
        else:
            self.indexed['_'] = self.indexed['_'].join(itv)
        return self

    def get_subscript(self, idx: str) -> 'IndexedLattice':
        """Get a specific indexed (sub)lattice element.

        :param idx: the target index
        :return: new lattice element indexing the retireved (sub)lattice element
        """
        indexed: Dict[str, Lattice] = dict()
        if idx in self.indexed:
            indexed[idx] = self.indexed[idx]
        else:
            indexed['_'] = self.default
        return type(self)(lattice=self.lattice, indexed=indexed, bound=self.bound)

    def set_slice(self, indexed: Dict[str, Lattice]) -> 'IndexedLattice':
        for idx, itv in indexed.items():
            self.set_subscript(idx, itv)
        return self

    def get_slice(self, idxs: List[str]) -> 'IndexedLattice':
        indexed: IndexedLattice = IndexedLattice(lattice=self.lattice).bottom()
        for idx in sorted(idxs):
            indexed = indexed.join(self.get_subscript(idx))
        return indexed

    def is_empty(self) -> bool:
        return len(self.indexed) == 1 and self.default.is_bottom()

    def is_nonempty(self) -> bool:
        return len(self.indexed) > 1 or not self.default.is_top()

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        items = sorted(self.indexed.items(), key=lambda x: x[0])
        return ', '.join('{}@{}'.format(idx, itv) for idx, itv in items)

    @copy_docstring(BottomMixin.top)
    def top(self):
        """The bottom lattice element is ``_ -> [-oo, +oo]``"""
        self._replace(type(self)(lattice=self.lattice, bound=self.bound))
        return self

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        return all(itv.is_top() for itv in self.indexed.values())

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'IndexedLattice') -> bool:
        # e.g., 0@[9, 9], 1@[1, 3], 2@[0, 0], _@[-oo, 4] ⊑ 0@[9, 10], 1@[-3, 3], _@[-oo, 9]
        mine: Set[str] = set(self.indexed.keys())
        yours: Set[str] = set(other.indexed.keys())
        result = yours.issubset(mine)   # other should fix fewer indexes than self
        if result:
            for idx, itv in self.indexed.items():
                if idx in other.indexes:    # self should fix stronger constraints than other
                    result = result and itv.less_equal(other.indexed[idx])
                else:
                    result = result and itv.less_equal(other.default)
        return result

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'IndexedLattice') -> 'IndexedLattice':
        # e.g., 1@[1, 1], 3@[3, 3], _@[-oo, 0] ⨆ 0@[0, 0], 1@[2, 2], _@[0, +oo]
        # = 1@[1, 2], _@[-oo, +oo]
        mine: Set[str] = set(self.indexed.keys())
        yours: Set[str] = set(other.indexed.keys())
        for idx in mine.intersection(yours):    # common indexes should be joined
            self.indexed[idx] = self.indexed[idx].join(other.indexed[idx])
        for idx in mine.difference(yours):  # join indexes fixed only by self with default
            self.indexed['_'] = self.indexed['_'].join(self.indexed[idx])
            del self.indexed[idx]
        for idx in yours.difference(mine):  # join indexes fixed only by other with default
            self.indexed['_'] = self.indexed['_'].join(other.indexed[idx])
        return self

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'IndexedLattice') -> 'IndexedLattice':
        default = self.default
        for idx, itv in self.indexed.items():
            if idx in other.indexed:    # common indexes should be met
                self.indexed[idx] = itv.meet(other.indexed[idx])
            else:               # meet indexes fixed only by self with default of other
                self.indexed[idx] = itv.meet(other.default)
        mine: Set[str] = set(self.indexed.keys())
        yours: Set[str] = set(other.indexed.keys())
        _yours: List[str] = sorted(list(yours.difference(mine)))
        for i in range(min(self.bound - self.size, len(_yours))):
            self.indexed[_yours[i]] = deepcopy(default).meet(other.indexed[_yours[i]])
        for j in range(self.bound, len(_yours)):
            self.indexed['_'] = self.indexed['_'].join(other.indexed[_yours[j]])
        for idx, itv in self.indexed.items():
            if idx != '_' and itv.is_bottom():
                return self.bottom()
        return self

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'IndexedLattice') -> 'IndexedLattice':
        mine: Set[str] = set(self.indexed.keys())
        yours: Set[str] = set(other.indexed.keys())
        for idx in mine.intersection(yours) - {'_'}:
            self.indexed[idx] = self.indexed[idx].widening(other.indexed[idx])
        _mine = self.default
        for idx in mine.difference(yours):
            _mine = _mine.join(self.indexed[idx])
        _yours = other.default
        for idx in yours.difference(mine):
            _yours = _yours.join(other.indexed[idx])
        self.indexed['_'] = _mine.widening(_yours)
        return self

    # string operations

    @copy_docstring(SequenceMixin._concat)
    def _concat(self, other: 'IndexedLattice') -> 'IndexedLattice':
        """
        .. note:: We assume here that the involved lattice elements are representing sequences.
        """
        if self.default.is_bottom():    # add indexes from other up to the bound
            yours: List[str] = sorted(list(other.indexed.keys()))[:-1]
            highest = sorted(list(self.indexed.keys()))[-2]
            for i in range(min(self.bound - self.size, len(yours))):
                next = str(int(highest) + i)
                self.indexed[next] = other.indexed[yours[i]]
            for j in range(min(self.bound - self.size, len(yours)), len(yours)):
                self.indexed['_'] = self.indexed['_'].join(other.indexed[yours[j]])
        else:   # join indexed from other with default
            for itv in other.indexed.values():
                self.indexed['_'] = self.indexed['_'].join(itv)
        return self
