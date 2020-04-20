"""
Indexed Lattice
===============

The elements of the lattice are a bounded number of indexed lattice elements.

:Author: Caterina Urban
"""
from ast import literal_eval
from copy import deepcopy
from math import inf
from typing import Dict, List, Set, Type

from lyra.abstract_domains.lattice import SequenceMixin, BottomMixin, Lattice
from lyra.core.expressions import Literal
from lyra.core.types import IntegerLyraType, LyraType, StringLyraType, FloatLyraType, \
    BooleanLyraType, TupleLyraType
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

    def __init__(self, lattice: Type[Lattice], index: Dict[str, Lattice] = None, bound: int = 3):
        """Indexed lattice creation.

        :param lattice: the (sub)lattice whose elements are to be indexed
        :param index: the initial index
        :param bound: bound on the size of the index
        """
        super().__init__()
        self._lattice: Type[Lattice] = lattice
        self._index: Dict[str, Lattice] = {self.default: self._lattice()}
        if index is not None:
            keys: List[str] = sorted(index.keys())
            for i in range(min(bound, len(keys))):          # index all possible elements
                self._index[keys[i]] = index[keys[i]]
            rest = self._lattice().bottom()
            for j in range(bound, len(keys)):               # join the rest of the elements
                rest = rest.join(index[keys[j]])
            if self.default in index:
                self._index[self.default] = self._index[self.default].join(rest)
            else:
                self._index[self.default] = rest
        self._bound: int = bound

    @classmethod
    def from_literal(cls, lattice: Type[Lattice], literal: Literal, bound: int = 3):
        if isinstance(literal.typ, StringLyraType):
            index = dict()
            for idx, item in enumerate(literal.val):
                if hasattr(lattice, 'from_literal'):
                    index[str(idx)] = lattice.from_literal(Literal(StringLyraType(), item))
                else:
                    index[str(idx)] = lattice().top()
            return cls(lattice, index, bound)
        return cls(lattice, None, 3)

    def __getitem__(self, idx: str) -> Lattice:
        return self.index.get(idx, self.index[self.default])

    def __setitem__(self, idx: str, itv: Lattice):
        if idx != self.default and (idx in self.index or self.size < self.bound):
            self.index[idx] = itv
        else:
            self.index[self.default] = self.index[self.default].join(itv)

    @property
    def lattice(self) -> Type[Lattice]:
        """Current (sub)lattice.

        :return: the (sub)lattice whose elements are indexed
        """
        return self._lattice

    @property
    def default(self) -> str:
        """Current default index.

        :return: the default index
        """
        return '_'

    @property
    def index(self) -> Dict[str, Lattice]:
        """Current index of (sub)lattice elements.

        :return: the current index
        """
        return self._index

    @property
    def used(self) -> List[str]:
        """Current used indexes.

        :return: the current used indexes (sorted)
        """
        items: List[str] = sorted(self.index.keys())
        if self.index[self.default].is_bottom():
            items.remove(self.default)   # exclude the (unused) default index
            return items
        return items

    @property
    def size(self) -> int:
        """Current number of indexed (sub)lattice elements.

        .. note:: the default index is not counted

        :return: the current number of indexed (sub)lattice elements
        """
        return len(self.index) - 1

    @property
    def bound(self) -> int:
        """Current bound on the indexed (sub)lattice elements.

        :return: the current bound on the indexed (sub)lattice elements
        """
        return self._bound

    def is_empty(self) -> bool:
        """Test whether the index is empty.

        :return: whether the index is empty
        """
        return len(self.index) == 1 and self.index[self.default].is_bottom()

    def is_nonempty(self) -> bool:
        """Test whether the index is non-empty.

        :return: whether the index is non-empty
        """
        return len(self.index) > 1 or not self.index[self.default].is_top()

    def summarize(self, keys: LyraType = None) -> 'Lattice':
        """Summarize the index into a single (sub)lattice element.

        :param keys: if give, type to use to also summarize the keys (default: None)
        :return: the (sub)lattice element representing the summary of the index
        """
        def do(lattice, typ, key, current: Lattice) -> Lattice:
            updated: Lattice = current
            if isinstance(typ, (BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType)):
                if hasattr(lattice, 'from_literal'):
                    literal = Literal(typ, key)
                    updated = updated.join(lattice.from_literal(literal))
                else:
                    updated = updated.join(lattice().top())
            else:
                assert isinstance(typ, TupleLyraType)
                val = literal_eval(key)
                for i, subtyp in enumerate(typ.typs):
                    updated = do(lattice, subtyp, val[i], updated)
            return updated

        summary: Lattice = self.lattice().bottom()
        if keys:
            for idx in self.used:
                if idx == self.default:
                    summary = summary.join(self.lattice().top())
                else:
                    summary = do(self.lattice, keys, idx, summary)

        for value in self.index.values():
            summary = summary.join(deepcopy(value))
        return summary

    def set_subscript(self, idx: str, itv: Lattice) -> 'IndexedLattice':
        """Set a specific index to a new (sub)lattice element.

        :param idx: the index to be set
        :param itv: the new (sub)lattice element
        :return: current lattice element modified to index the new (sub)lattice element
        """
        #TODO: redo
        if idx in self.index or self.size < self.bound:
            self.index[idx] = itv
        else:
            self.index['_'] = self.index['_'].join(itv)
        return self

    def get_subscript(self, idx: str) -> 'IndexedLattice':
        """Get a specific indexed (sub)lattice element.

        :param idx: the target index
        :return: new lattice element indexing the retireved (sub)lattice element
        """
        #TODO: redo
        indexed: Dict[str, Lattice] = dict()
        if idx in self.index:
            indexed[idx] = self.index[idx]
        else:
            indexed['_'] = self.index[self.default]
        return type(self)(lattice=self.lattice, index=indexed, bound=self.bound)

    def set_slice(self, indexed: Dict[str, Lattice]) -> 'IndexedLattice':
        for idx, itv in indexed.items():
            self.set_subscript(idx, itv)
        return self

    def get_slice(self, idxs: List[str]) -> 'IndexedLattice':
        indexed: IndexedLattice = IndexedLattice(lattice=self.lattice).bottom()
        for idx in sorted(idxs):
            indexed = indexed.join(self.get_subscript(idx))
        return indexed

    def refine(self, lattice: Lattice) -> 'IndexedLattice':
        for idx in self.index:
            self.index[idx] = self.index[idx].meet(deepcopy(lattice))
        return self

    def __repr__(self):
        if self.is_bottom():
            return "⊥"

        def order(key):
            return key if key != '_' else str(inf)

        items = sorted(self.index.items(), key=lambda x: order(x[0]))
        return ', '.join('{}@{}'.format(idx, itv) for idx, itv in items)

    @copy_docstring(BottomMixin.top)
    def top(self):
        """The top lattice element is ``_ -> [-oo, +oo]``"""
        self._replace(type(self)(lattice=self.lattice, bound=self.bound))
        return self

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        return all(itv.is_top() for itv in self.index.values())

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'IndexedLattice') -> bool:
        # e.g., 0@[9, 9], 1@[1, 3], 2@[0, 0], _@[-oo, 4] ⊑ 0@[9, 10], 1@[-3, 3], _@[-oo, 9]
        mine: Set[str] = set(self.index.keys())
        yours: Set[str] = set(other.index.keys())
        result = yours.issubset(mine)   # other should fix fewer indexes than self
        if result:
            for idx, itv in self.index.items():
                if idx in other.used:    # self should fix stronger constraints than other
                    result = result and itv.less_equal(other.index[idx])
                else:
                    result = result and itv.less_equal(other.index[self.default])
        return result

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'IndexedLattice') -> 'IndexedLattice':
        # e.g., 1@[1, 1], 3@[3, 3], _@[-oo, 0] ⨆ 0@[0, 0], 1@[2, 2], _@[0, +oo]
        # = 1@[1, 2], _@[-oo, +oo]
        mine: Set[str] = set(self.index.keys())
        yours: Set[str] = set(other.index.keys())
        for idx in mine.intersection(yours):    # common indexes should be joined
            self.index[idx] = self.index[idx].join(other.index[idx])
        for idx in mine.difference(yours):  # join indexes fixed only by self with default
            self.index['_'] = self.index['_'].join(self.index[idx])
            del self.index[idx]
        for idx in yours.difference(mine):  # join indexes fixed only by other with default
            self.index['_'] = self.index['_'].join(other.index[idx])
        return self

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'IndexedLattice') -> 'IndexedLattice':
        default = self.index[self.default]
        for idx, itv in self.index.items():
            if idx in other.index:    # common indexes should be met
                self.index[idx] = itv.meet(other.index[idx])
            else:               # meet indexes fixed only by self with default of other
                self.index[idx] = itv.meet(other.index[self.default])
        mine: Set[str] = set(self.index.keys())
        yours: Set[str] = set(other.index.keys())
        _yours: List[str] = sorted(list(yours.difference(mine)))
        for i in range(min(self.bound - self.size, len(_yours))):
            self.index[_yours[i]] = deepcopy(default).meet(other.index[_yours[i]])
        for j in range(self.bound, len(_yours)):
            self.index['_'] = self.index['_'].join(other.index[_yours[j]])
        for idx, itv in self.index.items():
            if idx != '_' and itv.is_bottom():
                return self.bottom()
        return self

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'IndexedLattice') -> 'IndexedLattice':
        mine: Set[str] = set(self.index.keys())
        yours: Set[str] = set(other.index.keys())
        for idx in mine.intersection(yours) - {'_'}:
            self.index[idx] = self.index[idx].widening(other.index[idx])
        _mine = self.index[self.default]
        for idx in mine.difference(yours):
            _mine = _mine.join(self.index[idx])
        _yours = other.index[other.default]
        for idx in yours.difference(mine):
            _yours = _yours.join(other.index[idx])
        self.index['_'] = _mine.widening(_yours)
        return self

    # string operations

    @copy_docstring(SequenceMixin._concat)
    def _concat(self, other: 'IndexedLattice') -> 'IndexedLattice':
        """
        .. note:: We assume here that the involved lattice elements are representing sequences.
        """
        if self.index[self.default].is_bottom():    # add indexes from other up to the bound
            yours: List[str] = sorted(list(other.index.keys()))[:-1]
            highest = sorted(list(self.index.keys()))[-2]
            for i in range(min(self.bound - self.size, len(yours))):
                self.index[str(int(highest) + i)] = other.index[yours[i]]
            for j in range(min(self.bound - self.size, len(yours)), len(yours)):
                self.index['_'] = self.index['_'].join(other.index[yours[j]])
        else:   # join indexed from other with default
            for itv in other.index.values():
                self.index['_'] = self.index['_'].join(itv)
        return self
