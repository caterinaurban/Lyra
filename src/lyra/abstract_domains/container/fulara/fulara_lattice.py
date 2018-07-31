"""
Fulara Lattice
========================

Generic lattice to abstract dictionaries as a set of abstract segments

:Authors: Lowis Engel
"""

from copy import deepcopy, copy
from typing import List, Tuple, Set, Type, Dict, Any

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier
from lyra.core.utils import copy_docstring


class FularaLattice(Lattice):
    """Fulara lattice element::

        set of abstract segments,
        represented by tuples (k,v) from two abstract domains K, V given as input
        (which abstract a set of keys and their corresponding values),
        s.t. (i) no two segments overlap (i.e. the meet of the keys is bottom)
             (ii) there are no empty segments (i.e. neither k nor v are bottom)

    Top: {(top, top)}
    Bottom: {}

    The default lattice element is Top, meaning the dictionary can contain anything.

    .. document private methods
    .. automethod:: FularaLattice._less_equal
    .. automethod:: FularaLattice._meet
    .. automethod:: FularaLattice._join
    .. automethod:: FularaLattice._widening
    """

    # use typing.Generic instead of domains as parameter?
    def __init__(self, key_domain: Type[Lattice], value_domain: Type[Lattice],
                 key_d_args: Dict[str, Any] = None, value_d_args: Dict[str, Any] = None,
                 segments: Set[Tuple[Lattice, Lattice]] = None):
        """
        :param key_domain: domain for abstraction of dictionary keys,
            ranges over the scalar variables and the special key variable v_k
        :param value_domain: domain for abstraction of dictionary values,
            ranges over the scalar variables and the special value variable v_v
        :param key_d_args: arguments for the key_domain
        :param value_d_args: arguments for the value_domain
        :param segments: initial set of abstract segments; if None, a top segment is created
        """
        # TODO: segments internally as List?

        if key_d_args is None:
            key_d_args = {}
        if value_d_args is None:
            value_d_args = {}

        super().__init__()
        self._k_domain = key_domain
        self._k_d_args = key_d_args
        self._v_domain = value_domain
        self._v_d_args = value_d_args

        if segments is None:    # default element
            self._segments = {(key_domain(**key_d_args).top(), value_domain(**value_d_args).top())}
        else:
            # for s in segments:      # TODO: remove?
            #     if len(s) != 2:
            #         raise TypeError(f"Segment {s} needs to have exactly two elements,
            #                         but has {len(s)}")
            #     if not isinstance(s[0], key_domain):
            #         raise TypeError(f"The key type of the segment {s}
            #                         does not match the provided key domain {key_domain}")
            #     if not isinstance(s[1], value_domain):
            #         raise TypeError(f"The value type of the segment {s}
            #                         does not match the provided value domain {value_domain}")
            self._segments = segments

    @property
    def k_domain(self) -> Type[Lattice]:
        """Domain for the abstract keys."""
        return self._k_domain

    @property
    def v_domain(self) -> Type[Lattice]:
        """Domain for the abstract values."""
        return self._v_domain

    @property
    def k_d_args(self):
        """Arguments for the key domain given in constructor"""
        return self._k_d_args

    @property
    def v_d_args(self):
        """Arguments for the value domain given in constructor"""
        return self._v_d_args

    @property
    def segments(self) -> Set[Tuple[Lattice, Lattice]]:
        """Set of all abstract segments."""
        return self._segments

    def sorted_segments(self) -> List[Tuple[Lattice, Lattice]]:
        """List of all abstract segments ordered by their keys"""
        return sorted(self.segments, key=lambda t: t[0])

    def __repr__(self):
        str_segments = map(repr, self.sorted_segments())
        result = "{" + ", ".join(str_segments) + "}"
        return result

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'FularaLattice':
        """The bottom lattice element is ``{}``."""
        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args, set()))
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'FularaLattice':
        """The top lattice element is ``{(top, top)}``."""
        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args))
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return len(self.segments) == 0

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        if len(self.segments) == 1:
            segment = next(iter(self.segments))     # 'get' (work-around to not use pop)
            return segment[0].is_top() and segment[1].is_top()
        return False

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'FularaLattice') -> bool:
        if self.k_domain != other.k_domain:
            raise TypeError(f"Cannot compare dictionary abstractions with different "
                            f"key abstractions ({self.k_domain}, {other.k_domain})")
        if self.v_domain != other.v_domain:
            raise TypeError(f"Cannot compare dictionary abstractions with different "
                            f"value abstractions ({self.v_domain}, {other.v_domain})")

        # le <=> same or more 'boundaries'
        if self.segments == other.segments:     # TODO: needed (efficiency?
            return True
        else:
            # all segments of self need to be contained in some segment of other
            # & their value must be less_equal
            for (k1, v1) in self.segments:
                for (k2, v2) in other.segments:
                    k_meet = deepcopy(k1).meet(k2)
                    if not k_meet.is_bottom():      # segments overlap
                        if k1.less_equal(k2) and v1.less_equal(v2):
                            break   # self segment can only be contained in one other segment
                        return False  # (k1, v1) not fully contained in (k2, v2)
                else:   # (k1, v1) does not overlap with any segment of other
                    return False

            return True

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'FularaLattice') -> 'FularaLattice':
        """Point-wise meet of overlapping segments"""
        self_segments = copy(self.segments)
        other_segments = copy(other.segments)
        # skip equal segments:
        same_segments = self_segments.intersection(other_segments)
        self_segments.difference_update(same_segments)
        other_segments.difference_update(same_segments)
        new_segments = same_segments
        for (k1, v1) in self_segments:
            for (k2, v2) in other_segments:
                k_meet = deepcopy(k1).meet(deepcopy(k2))
                if not k_meet.is_bottom():
                    v_meet = deepcopy(v1).meet(deepcopy(v2))
                    if not v_meet.is_bottom():
                        new_segments.add((k_meet, v_meet))

        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args, new_segments))
        return self

    def d_norm_own(self):
        """Applies d_norm to own segment set"""
        self._segments = d_norm(self.segments)

    @copy_docstring(Lattice._join)
    def _join(self, other: 'FularaLattice') -> 'FularaLattice':
        # dnorm(union(segments))
        if len(self.segments) > len(other.segments):
            new_segments = d_norm(other.segments, self.segments)
        else:
            new_segments = d_norm(self.segments, other.segments)
        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args, new_segments))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'FularaLattice') -> 'FularaLattice':
        # imprecise version

        segment_set = copy(self.segments)     # cond. 2
        o_add_segment = False   # other has a segment, which does not overlap with any of self
        for o in other.segments:
            o_overlaps = False
            for s in self.segments:
                s_meet_o = deepcopy(s[0]).meet(o[0])
                if not s_meet_o.is_bottom():    # segments overlap (cond. 1)
                    o_overlaps = True
                    # overlaps with some o (not cond. 2) -> needs to be widened
                    segment_set.discard(s)
                    # point-wise widening
                    r = (deepcopy(s[0]).widening(deepcopy(o[0])),
                         deepcopy(s[1]).widening(deepcopy(o[1])))
                    segment_set.add(r)
            if not o_overlaps:
                segment_set.add(o)      # cond. 3 (key will be set to top later)
                o_add_segment = True

        result_set = set()
        if o_add_segment:   # cond. 3, not using d_norm for efficiency
            # join everything to one top segment (extreme widening)
            value_list = [s[1] for s in segment_set]
            top_segment = (self.k_domain(**self.k_d_args).top(),
                           self.v_domain(**self.v_d_args).big_join(value_list))
            result_set.add(top_segment)
        else:  # o does not have an additional non-overlapping segment
            result_set = d_norm(segment_set)

        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args, result_set))
        return self

    # helper      # TODO: put helpers in DictContentDomain?
    def partition_add(self, key: Lattice, value: Lattice):
        """Adds the given key-value-pair to the segments (if key/value are not bottom)
        and removes all overlapping parts of other segments (computes a new partition).
        (strong update)"""
        old_segments = copy(self.segments)
        for s in old_segments:
            s_meet_key = deepcopy(s[0]).meet(key)
            if not s_meet_key.is_bottom():
                # segments overlap -> partition, s.t. overlapping part is removed
                self.segments.remove(s)
                # TODO: require KeyWrapper?
                non_overlapping = {(m, s[1]) for m in s[0].decomp(s[0], key) if not m.is_bottom()}
                self.segments.update(non_overlapping)       # union
        if not (key.is_bottom() or value.is_bottom()):
            self.segments.add((key, value))

    def normalized_add(self, key: Lattice, value: Lattice):
        """Adds the given key-value-pair to the segment set (if key/value are not bottom)
        and applies the d_norm function (so the new segment may get joined with existing ones)
        (weak update)"""
        if not (key.is_bottom() or value.is_bottom()):
            self._segments = d_norm({(key, value)}, self.segments)

    # helper
    def forget_variable(self, variable: VariableIdentifier):
        for (k, v) in self.segments:
            k.forget_variable(variable)
            v.forget_variable(variable)

    # helper
    def get_keys_joined(self) -> Lattice:
        result = self.k_domain(**self.k_d_args).bottom()
        for (k, v) in self.segments:
            result.join(deepcopy(k))
        return result

    # helper
    def get_values_joined(self) -> Lattice:
        result = self.v_domain(**self.v_d_args).bottom()
        for (k, v) in self.segments:
            result.join(deepcopy(v))
        return result


def d_norm(segment_set: Set[Tuple[Lattice, Lattice]],
           known_disjoint: Set[Tuple[Lattice, Lattice]] = None) \
        -> Set[Tuple[Lattice, Lattice]]:
    """disjoint normalization function:
    Computes a partition such that no two abstract keys overlap (i.e. their meet is bottom)
    (and the keys are minimal)"""
    # TODO: make faster? (sorted segments?)
    # TODO: assert same domains?
    if known_disjoint is None:
        result_set = set()
    else:
        result_set = copy(known_disjoint)
    for s in segment_set:
        remove_set = set()
        for r in result_set:
            s_meet_r = deepcopy(s[0]).meet(r[0])
            if not s_meet_r.is_bottom():  # not disjoint -> join segments
                s = (deepcopy(s[0]).join(deepcopy(r[0])), deepcopy(s[1]).join(deepcopy(r[1])))
                remove_set.add(r)
        result_set.difference_update(remove_set)
        result_set.add(s)

    return result_set
