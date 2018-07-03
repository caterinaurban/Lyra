from collections import defaultdict
from copy import deepcopy
from typing import List, Tuple, Set, Type, Callable, Dict, Any, Union

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.relational_store import RelationalStore
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression
from lyra.core.types import DictLyraType, LyraType, BooleanLyraType, IntegerLyraType, \
    FloatLyraType, StringLyraType

from lyra.core.utils import copy_docstring


class DictSegmentLattice(Lattice):
    """Dictionary segment lattice element::

        set of abstract segments,
            represented by tuples (k,v) from two abstract domains K, V given as input
            (which abstract a set of keys and their corresponding values),
            s.t. (i) no two segments overlap (i.e. the meet of the keys is bottom)
                 (ii) there are no empty segments (i.e. neither k nor v are bottom)

        Top: {(top, top)}
        Bottom: {}

    The default lattice element is Top, meaning the dictionary can contain anything.        #TODO: ?

    .. document private methods
    .. automethod:: DictSegmentLattice._less_equal
    .. automethod:: DictSegmentLattice._meet
    .. automethod:: DictSegmentLattice._join
    .. automethod:: DictSegmentLattice._widening
    """
    def __init__(self, key_domain: Type[Lattice], value_domain: Type[Lattice],      # TODO: use typing.Generic
                 key_d_args: Dict[str, Any] = {}, value_d_args: Dict[str, Any] = {},
                 segments: Set[Tuple[Lattice, Lattice]] = None):       # TODO: Set?
        # TODO: document
        super().__init__()
        self._k_domain = key_domain
        self._k_d_args = key_d_args
        self._v_domain = value_domain
        self._v_d_args = value_d_args

        if segments is None:    # default element
            self._segments = {(key_domain(**key_d_args).top(), value_domain(**value_d_args).top())}   #TODO: correct, constructor without arg?
        else:
            for s in segments:      # TODO: remove?
                if len(s) != 2:
                    raise TypeError(f"Segment {s} needs to have exactly two elements, but has {len(s)}")
                if not isinstance(s[0], key_domain):
                    raise TypeError(f"The key type of the segment {s} does not match the provided key domain {key_domain}")
                if not isinstance(s[1], value_domain):
                    raise TypeError(f"The value type of the segment {s} does not match the provided value domain {value_domain}")
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
    def segments(self) -> Set[Tuple[Lattice, Lattice]]:
        """List of all abstract segments."""
        return self._segments

    def __repr__(self):
        return repr(self.segments)

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'DictSegmentLattice':
        """The bottom lattice element is ``{}``."""
        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self._k_d_args, self._v_d_args, set()))
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'DictSegmentLattice':
        """The top lattice element is ``{(top, top)}``."""
        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self._k_d_args, self._v_d_args))
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return len(self.segments) == 0

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        if len(self.segments) == 1:
            segment = next(iter(self.segments))     # 'get' (work-around to not use pop)
            return segment[0].is_top() and segment[1].is_top()
        else:
            return False

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'DictSegmentLattice') -> bool:
        if self.k_domain != other.k_domain:
            raise TypeError(f"Cannot compare dictionary abstractions with different key abstractions ({self.k_domain}, {other.k_domain})")
        if self.v_domain != other.v_domain:
            raise TypeError(f"Cannot compare dictionary abstractions with different value abstractions ({self.v_domain}, {other.v_domain})")

        # le <=> same or more 'boundaries'
        if self.segments == other.segments:
            return True
        if len(self.segments) > len(other.segments):  # more segments => more 'boundaries'
            return True
        else:
            raise NotImplementedError("The comparison between dictionary abstractions with the same number of segments is not yet implemented")

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'DictSegmentLattice') -> 'DictSegmentLattice':
        """Point-wise meet of overlapping segments"""
        new_segments = set()
        for (k1, v1) in self.segments:
            for (k2, v2) in other.segments:
                k_meet = k1.meet(k2)
                if not k_meet.is_bottom():
                    v_meet = v1.meet(v2)
                    if not v_meet.is_bottom():
                        new_segments.add((k_meet, v_meet))

        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self._k_d_args, self._v_d_args, new_segments))
        return self

    def d_norm(self, segment_set: Set[Tuple[Lattice, Lattice]],
               known_disjoint: Set[Tuple[Lattice, Lattice]] = set()) -> Set[Tuple[Lattice, Lattice]]:
        """disjoint normalization function:
        Computes a partition such that no two abstract keys overlap (i.e. their meet is bottom)
        (and the keys are minimal)"""
        # TODO: make faster? (sorted segments?)
        # TODO: assert same domains?
        result_set = known_disjoint
        for s in segment_set:
            for r in result_set:
                s_meet_r = deepcopy(s[0]).meet(r[0])
                if not s_meet_r.is_bottom():  # not disjoint -> join segments
                    result_set.remove(r)
                    s = (s[0].join(r[0]), s[1].join(r[1]))  # TODO: don't assign s?
            result_set.add(s)

        return result_set

    @copy_docstring(Lattice._join)
    def _join(self, other: 'DictSegmentLattice') -> 'DictSegmentLattice':
        # dnorm(union(segments))
        if len(self.segments) > len(other.segments):
            new_segments = self.d_norm(other.segments, self.segments)
        else:
            new_segments = self.d_norm(self.segments, other.segments)
        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self._k_d_args, self._v_d_args, new_segments))
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'DictSegmentLattice') -> 'DictSegmentLattice':
        # imprecise version

        segment_set = self.segments     # cond. 2
        o_add_segment = False   # other has a segment, which does not overlap with any of self
        for o in other.segments:
            o_overlaps = False
            for s in self.segments:
                s_meet_o = deepcopy(s[0]).meet(o[0])
                if not s_meet_o.is_bottom():    # segments overlap (cond. 1)
                    o_overlaps = True
                    segment_set.discard(s)      # overlaps with some o (not cond. 2) -> needs to be widened
                    # point-wise widening
                    r = deepcopy(s)
                    r = (r[0].widening(o[0]), r[1].widening(o[1]))
                    segment_set.add(r)
            if not o_overlaps:
                segment_set.add(o)      # cond. 3 (key will be set to top later)
                o_add_segment = True

        result_set = set()
        if o_add_segment:   # cond. 3, not using d_norm for efficiency
            # join everything to one top segment (extreme widening)
            value_list = [s[1] for s in segment_set]
            top_segment = (self.k_domain().top(), self.v_domain().big_join(value_list))             # TODO: wrong usage of top?
            result_set.add(top_segment)
        else:  # o does not have an additional non-overlapping segment
            result_set = self.d_norm(segment_set)

        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self.v_domain, self._k_d_args, self._v_d_args, result_set))
        return self


class DictContentState(State):
    """Dictionary content analysis state.
    An element of the dictionary content abstract domain.

    Map from each program variable to its liveness status.
    All program variables are *dead* by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: LivenessState._assign
    .. automethod:: LivenessState._assume
    .. automethod:: LivenessState._output
    .. automethod:: LivenessState._substitute
    """
    def __init__(self, variables: List[VariableIdentifier]):
        """Map each program variable to its liveness status.

        :param variables: list of program variables
        """
        lattices = defaultdict(lambda: LivenessLattice)
        super().__init__(variables, lattices)

    @copy_docstring(Store.is_bottom)
    def is_bottom(self) -> bool:
        """The current store is bottom if `all` of its variables map to a bottom element."""
        return all(element.is_bottom() for element in self.store.values())

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'LivenessState':
        for identifier in condition.ids():
            if isinstance(identifier, VariableIdentifier):
                self.store[identifier].top()
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'LivenessState':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'LivenessState':
        if isinstance(left, VariableIdentifier):
            self.store[left].bottom()
            for identifier in right.ids():
                if isinstance(identifier, VariableIdentifier):
                    self.store[identifier].top()
                else:
                    error = f"Substitution with {right} is not implemented!"
                    raise NotImplementedError(error)
            return self
        error = f"Substitution for {left} is not yet implemented!"
        raise NotImplementedError(error)