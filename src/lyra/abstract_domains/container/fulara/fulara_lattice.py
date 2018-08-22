"""
Fulara Lattice
========================

Generic lattice to abstract dictionaries as a set of abstract segments

:Authors: Lowis Engel
"""
import itertools
from copy import deepcopy, copy
from typing import Tuple, Set, Type, Dict, Any

from lyra.abstract_domains.container.fulara.key_wrapper import KeyWrapper
from lyra.abstract_domains.lattice import Lattice, BottomMixin
from lyra.core.expressions import VariableIdentifier
from lyra.core.utils import copy_docstring


class FularaLattice(BottomMixin):
    """Fulara lattice element::

        set of abstract segments,
        represented by tuples (k,v) from two abstract domains K, V given as input
        (which abstract a set of keys and their corresponding values),
        s.t. (i) no two segments overlap (i.e. the meet of the keys is bottom)
             (ii) there are no empty segments (i.e. neither k nor v are bottom)

    Top: {(top, top)}
        /     |     \
             ...

           \  |  /
             {}
              |
    Bottom:   ⊥

    The default lattice element is Top, meaning the dictionary can contain anything.

    .. document private methods
    .. automethod:: FularaLattice._less_equal
    .. automethod:: FularaLattice._meet
    .. automethod:: FularaLattice._join
    .. automethod:: FularaLattice._widening
    """

    # use typing.Generic instead of domains as parameter?
    def __init__(self, key_domain: Type[KeyWrapper], value_domain: Type[Lattice],
                 key_d_args: Dict[str, Any] = None, value_d_args: Dict[str, Any] = None,
                 segments: Set[Tuple[KeyWrapper, Lattice]] = None):
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

        super().__init__()
        self._k_domain = key_domain
        self._k_d_args = key_d_args or {}
        self._v_domain = value_domain
        self._v_d_args = value_d_args or {}

        if segments is None:    # default element
            self._segments = {(key_domain(**self.k_d_args).top(),
                               value_domain(**self.v_d_args).top())}
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
        # TODO: add possibility to create bottom element?

    @property
    def k_domain(self):
        """Domain for the abstract keys."""
        return self._k_domain

    @property
    def v_domain(self):
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
    def segments(self):
        """Set of all abstract segments."""
        if not self.is_bottom():
            return self._segments

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        sorted_segments = sorted(self.segments, key=lambda t: t[0])
        str_segments = map(repr, sorted_segments)
        result = "{" + ", ".join(str_segments) + "}"
        return result

    @copy_docstring(BottomMixin.top)
    def top(self) -> 'FularaLattice':
        """The top lattice element is ``{(top, top)}``."""
        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args))
        return self

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        if not self.is_bottom() and len(self.segments) == 1:
            segment = next(iter(self.segments))     # 'get' (work-around to not use pop)
            return segment[0].is_top() and segment[1].is_top()
        return False

    def empty(self) -> 'FularaLattice':
        """Abstraction of an empty dictionary (=> empty segment set)"""
        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args, set()))
        return self

    def is_empty(self) -> bool:
        """Test whether the abstraction is empty (has an empty segment set)"""
        if not self.is_bottom():
            return len(self.segments) == 0
        return False

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'FularaLattice') -> bool:
        if self.k_domain != other.k_domain:
            raise TypeError(f"Cannot compare dictionary abstractions with different "
                            f"key abstractions ({self.k_domain}, {other.k_domain})")
        if self.v_domain != other.v_domain:
            raise TypeError(f"Cannot compare dictionary abstractions with different "
                            f"value abstractions ({self.v_domain}, {other.v_domain})")

        # le <=> same or more 'boundaries'
        if self.segments == other.segments:     # TODO: needed (efficiency?)
            return True
        else:
            # all segments of self need to be contained in some segment of other
            # & their value must be less_equal
            for (k1, v1) in self.segments:
                for (k2, v2) in other.segments:
                    k_meet = deepcopy(k1).meet(k2)
                    if not k_meet.key_is_bottom():      # segments overlap
                        if k1.less_equal(k2) and v1.less_equal(v2):
                            break   # self segment can only be contained in one other segment
                        return False  # (k1, v1) not fully contained in (k2, v2)
                else:   # (k1, v1) does not overlap with any segment of other
                    return False

            return True

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'FularaLattice') -> 'FularaLattice':
        """Point-wise meet of overlapping segments"""
        new_segments = set()
        other_segments = copy(other.segments)
        for (k1, v1) in self.segments:
            for (k2, v2) in other_segments:
                if (k1, v1) == (k2, v2):
                    new_segments.add((k1, v1))
                    other_segments.remove((k2, v2))     # cannot overlap again
                    break   # there cannot be more segments in other that overlap with (k1, v1)

                k_meet = deepcopy(k1).meet(deepcopy(k2))
                if not k_meet.key_is_bottom():
                    v_meet = deepcopy(v1).meet(deepcopy(v2))
                    if not v_meet.value_is_bottom():
                        new_segments.add((k_meet, v_meet))

        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args, new_segments))
        return self

    def d_norm_own(self):
        """Applies d_norm to own segment set"""
        if not self.is_bottom():
            self._segments = d_norm(self.segments)

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'FularaLattice') -> 'FularaLattice':
        # dnorm(union(segments))
        if len(self.segments) > len(other.segments):
            new_segments = d_norm(other.segments, self.segments)
        else:
            new_segments = d_norm(self.segments, other.segments)
        self._replace(FularaLattice(self.k_domain, self.v_domain,
                                    self.k_d_args, self.v_d_args, new_segments))
        return self

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'FularaLattice') -> 'FularaLattice':
        # imprecise version
        segment_set = copy(self.segments)     # cond. 2
        o_add_segment = False   # other has a segment, which does not overlap with any of self
        for o in other.segments:
            o_overlaps = False
            for s in self.segments:
                s_meet_o = deepcopy(s[0]).meet(o[0])
                if not s_meet_o.key_is_bottom():    # segments overlap (cond. 1)
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

    # helper
    def partition_add(self, key: KeyWrapper, value: Lattice):
        """Adds the given key-value-pair to the segments (if key/value are not bottom)
        and removes all overlapping parts of other segments (computes a new partition).
        (strong update)"""
        if not self.is_bottom():
            new_segments = copy(self.segments)
            for s in self.segments:
                s_meet_key = deepcopy(s[0]).meet(key)
                if not s_meet_key.key_is_bottom():
                    # segments overlap -> partition, s.t. overlapping part is removed
                    decompostion = s[0].decomp(key)
                    if decompostion is None:
                        # strong update not possible -> perform weak update (without partitioning)
                        self.normalized_add(key, value)
                        return
                    new_segments.remove(s)
                    non_overlapping = {(m, s[1]) for m in decompostion if not m.is_bottom()}
                    new_segments.update(non_overlapping)       # union
            if not (key.is_bottom() or value.is_bottom()):
                new_segments.add((key, value))
            self.segments.clear()
            self.segments.update(new_segments)

    def partition_update(self, disjoint_segments: Set[Tuple[KeyWrapper, Lattice]]):
        """Adds the given segments to self.segments.
        Joins overlapping parts with already present segments,
        creating new segments containing only the overlap
        (weak update with partitioning)"""
        if not self.is_bottom():
            rest_new = {s for s in disjoint_segments  # only add if not bottom
                        if not (s[0].key_is_bottom() or s[1].is_bottom())}
            old_segments = copy(self.segments)
            for s in old_segments:
                self.segments.remove(s)     # TODO: efficiency
                rest_s = {s}
                todo = itertools.product(copy(rest_new), copy(rest_s))
                while True:
                    try:
                        (new, old) = next(todo)
                    except StopIteration:   # no combination left to check
                        break

                    if new[0] == old[0]:     # for efficiency
                        rest_new.remove(new)
                        rest_s.remove(old)
                        value = deepcopy(new[1]).join(old[1])
                        self.segments.add((old[0], value))
                        todo = itertools.product(copy(rest_new), copy(rest_s))
                        continue

                    overlap = deepcopy(new[0]).meet(deepcopy(old[0]))       # TODO: deepcopy old?
                    if not overlap.key_is_bottom():
                        rest_new.remove(new)
                        if not new[1].less_equal(old[1]):  # will be changed by join -> partition
                            rest_s.remove(old)
                            # segments overlap -> partition, s.t. only overlapping part is updated
                            # TODO: require KeyWrapper?
                            # remaining parts of 'old'
                            non_overlap = {(m, old[1]) for m in old[0].decomp(new[0])
                                           if not m.key_is_bottom()}
                            rest_s.update(non_overlap)

                            # TODO: deepcopy old?
                            new_value = deepcopy(new[1]).join(deepcopy(old[1]))
                            self.segments.add((overlap, new_value))
                        elif overlap == old[0]:     # completely covered -> can keep segment
                            self.segments.add(old)
                            rest_s.remove(old)
                        # compute remaining parts of 'new'
                        rest_new.update({(m, new[1]) for m in new[0].decomp(overlap)
                                         if not m.key_is_bottom()})
                        # recompute product:
                        todo = itertools.product(copy(rest_new), copy(rest_s))

                self.segments.update(rest_s)    # add remaining parts of s (unmodified)
            self.segments.update(rest_new)    # add non-overlapping parts of the new segment(s)

    def normalized_add(self, key: KeyWrapper, value: Lattice):
        """Adds the given key-value-pair to the segment set (if key/value are not bottom)
        and applies the d_norm function (so the new segment may get joined with existing ones)
        (weak update without partitioning)"""
        if not self.is_bottom():
            if not (key.key_is_bottom() or value.is_bottom()):
                self._segments = d_norm({(key, value)}, self.segments)

    # helper
    def forget_variable(self, variable: VariableIdentifier):
        """Forgets the variable in all segments (key & value part)"""
        if not self.is_bottom():
            for (k, v) in self.segments:
                k.forget_variable(variable)
                v.forget_variable(variable)

    # helper
    def get_keys_joined(self) -> KeyWrapper:
        """Returns the join of all key abstractions of current segments"""
        if not self.is_bottom():
            result = self.k_domain(**self.k_d_args).bottom()
            for (k, v) in self.segments:
                result.join(deepcopy(k))
            return result

    # helper
    def get_values_joined(self) -> Lattice:
        """Returns the join of all value abstractions of current segments"""
        if not self.is_bottom():
            result = self.v_domain(**self.v_d_args).bottom()
            for (k, v) in self.segments:
                result.join(deepcopy(v))
            return result


def d_norm(segment_set: Set[Tuple[KeyWrapper, Lattice]],
           known_disjoint: Set[Tuple[KeyWrapper, Lattice]] = None) \
        -> Set[Tuple[KeyWrapper, Lattice]]:
    """disjoint normalization function:
    Computes a partition such that no two abstract keys overlap (i.e. their meet is bottom)
    (and the keys are minimal)"""
    # TODO: make faster? (sorted segments?)
    # TODO: assert same domains?
    if known_disjoint:      # not empty & not None
        result_set = copy(known_disjoint)
    else:
        result_set = set()

    for s in segment_set:
        remove_set = set()
        for r in result_set:
            s_meet_r = deepcopy(s[0]).meet(r[0])
            if not s_meet_r.key_is_bottom():  # not disjoint -> join segments
                s = (deepcopy(s[0]).join(deepcopy(r[0])), deepcopy(s[1]).join(deepcopy(r[1])))
                remove_set.add(r)
        result_set.difference_update(remove_set)
        result_set.add(s)

    return result_set
