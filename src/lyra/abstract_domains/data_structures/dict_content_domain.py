from collections import defaultdict
from copy import deepcopy, copy
from typing import List, Tuple, Set, Type, Callable, Dict, Any, Union

from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.relational_store import RelationalStore
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, Slicing, \
    DictDisplay
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
                 key_decomp_function: Callable[[Lattice, Lattice], Set[Lattice]],
                 key_d_args: Dict[str, Any] = {}, value_d_args: Dict[str, Any] = {},
                 segments: Set[Tuple[Lattice, Lattice]] = None):       # TODO: Set?
        # TODO: document
        super().__init__()
        self._k_domain = key_domain
        self._k_d_args = key_d_args
        self._v_domain = value_domain
        self._v_d_args = value_d_args

        self._k_decomp = key_decomp_function

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

    @property
    def k_decomp(self) -> Callable[[Lattice, Lattice], Set[Lattice]]:
        """Function to decompose a abstract key (first arg) into a set of abstract keys,
        that does not contain/overlap with the key given in the second argument."""
        return self._k_decomp

    def __repr__(self):     # TODO: use join?
        result = "{"
        first = True
        for (k,v) in self.segments:
            if first:
                first = False
            else:
                result += ", "
            result += f"({k};  {v})"
        result += "}"
        return result

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'DictSegmentLattice':
        """The bottom lattice element is ``{}``."""
        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self.k_decomp, self._k_d_args, self._v_d_args, set()))
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'DictSegmentLattice':
        """The top lattice element is ``{(top, top)}``."""
        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self.k_decomp, self._k_d_args, self._v_d_args))
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

        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self.k_decomp, self._k_d_args, self._v_d_args, new_segments))
        return self

    def d_norm(self, segment_set: Set[Tuple[Lattice, Lattice]],
               known_disjoint: Set[Tuple[Lattice, Lattice]] = None) -> Set[Tuple[Lattice, Lattice]]:
        """disjoint normalization function:
        Computes a partition such that no two abstract keys overlap (i.e. their meet is bottom)
        (and the keys are minimal)"""
        # TODO: make faster? (sorted segments?)
        # TODO: assert same domains?
        if known_disjoint is None:
            result_set = set()
        else:
            result_set = known_disjoint
        for s in segment_set:
            remove_set = set()
            for r in result_set:
                s_meet_r = deepcopy(s[0]).meet(r[0])
                if not s_meet_r.is_bottom():  # not disjoint -> join segments
                    remove_set.add(r)
                    s = (s[0].join(r[0]), s[1].join(r[1]))  # TODO: don't assign s?
            result_set.difference_update(remove_set)
            result_set.add(s)

        return result_set

    def d_norm_own(self):
        """Applies d_norm to own segment set"""
        self._segments = self.d_norm(self.segments)

    @copy_docstring(Lattice._join)
    def _join(self, other: 'DictSegmentLattice') -> 'DictSegmentLattice':
        # dnorm(union(segments))
        if len(self.segments) > len(other.segments):
            new_segments = self.d_norm(other.segments, self.segments)
        else:
            new_segments = self.d_norm(self.segments, other.segments)
        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self.k_decomp, self._k_d_args, self._v_d_args, new_segments))
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

        self.replace(DictSegmentLattice(self.k_domain, self.v_domain, self.k_decomp, self._k_d_args, self._v_d_args, result_set))
        return self

    # helper for strong updates with partitioning
    def partition_add(self, key: Lattice, value: Lattice):
        old_segments = copy(self.segments)
        for s in old_segments:
            s_meet_key = deepcopy(s[0]).meet(key)
            if not s_meet_key.is_bottom():  # segments overlap -> partition, s.t. overlapping part is removed
                self.segments.remove(s)
                non_overlapping = {(m, s[1]) for m in self.k_decomp(s[0], key) if not m.is_bottom()}       # TODO: add decomp in init
                self.segments.update(non_overlapping)
        if not (key.is_bottom() or value.is_bottom()):  # TODO: at more places?
            self.segments.add((key, value))

    # helper for weak updates without partitioning
    def normalized_add(self, key: Lattice, value: Lattice):
        self._segments = self.d_norm({(key, value)}, self.segments)


    def forget_var(self, var: VariableIdentifier):
        for (k,v) in self.segments:
            k.forget_var(var)
            v.forget_var(var)


class BoolLattice(Lattice):
    """Boolean lattice element (True/False),
        where True overapproximates concrete True values
        (so True -> may be True in the concrete

    (Maybe) True
          |
        False

    The default element is True (top)

    .. document private methods
    .. automethod:: DictSegmentLattice._less_equal
    .. automethod:: DictSegmentLattice._meet
    .. automethod:: DictSegmentLattice._join
    .. automethod:: DictSegmentLattice._widening
    """
    def __init__(self, value: bool = True):
        super().__init__()
        self._value = value

    @property
    def value(self):
        """Current boolean value."""
        return self._value

    def __repr__(self):
        return repr(self._value)

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        """The bottom lattice element is ``False``."""
        self.replace(BoolLattice(False))
        return self

    @copy_docstring(Lattice.top)
    def top(self):
        """The top lattice element is ``True``."""
        self.replace(BoolLattice())
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return not self._value

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self._value

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'BoolLattice') -> bool:
        pass    # already handled by less_equal (only false for self = top, other = bottom)

    @copy_docstring(Lattice._join)
    def _join(self, other: 'BoolLattice') -> 'BoolLattice':
        pass    # already handled by join

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'BoolLattice'):
        pass    # already handled by meet

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'BoolLattice'):
        pass    # already handled by widening

    def forget_var(self, var: VariableIdentifier):
        pass    # no variables stored


class DictContentState(State):
    """Dictionary content analysis state.
    An element of the dictionary content abstract domain.

    It consists of the following 3 elements:
    - Abstract state from a given domain A over all scalar variables,
        abstracting their values
    - Map from all dictionary variables to a DictSegmentLattice-element with a given key domain K
        and value domain V, abstracting the contents of the dictionaries
    - Map from all dictionary variables to a DictSegmentLattice-element with a given key domain K and the Booleans as value domain,
        abstracting the initialization info of the dictionary elements
        (True = may be uninitialized, False/Not present = def. initialized)

    Everything is Top by default        # TODO

    .. document private methods
    .. automethod:: LivenessState._assign
    .. automethod:: LivenessState._assume
    .. automethod:: LivenessState._output
    .. automethod:: LivenessState._substitute
    """

    # here the Union type means a logical AND: the domain should inherit from both RelationalStore and State
    def __init__(self, scalar_domain: Type[Union[RelationalStore, State]],
                 key_domain: Type[Union[RelationalStore, State]], value_domain: Type[Union[RelationalStore, State]],
                 key_decomp_function: Callable[[Lattice, Lattice], Set[Lattice]],
                 scalar_vars: List[VariableIdentifier] = None, dict_vars: List[VariableIdentifier] = None,
                 scalar_k_conv: Callable[[Union[RelationalStore, State]], Union[RelationalStore, State]] = lambda x: x,
                 k_scalar_conv: Callable[[Union[RelationalStore, State]], Union[RelationalStore, State]] = lambda x: x,
                 scalar_v_conv: Callable[[Union[RelationalStore, State]], Union[RelationalStore, State]] = lambda x: x,
                 v_scalar_conv: Callable[[Union[RelationalStore, State]], Union[RelationalStore, State]] = lambda x: x):
        """Map each program variable to its liveness status.

        :param scalar_domain: domain for abstraction of scalar variable values, ranges over the scalar variables #TODO: separate per type?
        :param key_domain: domain for abstraction of dictionary keys; (possibly) ranges over scalar variables and definetly has a special key variable v_k
        :param value_domain: domain for abstraction of dictionary values; (possibly) ranges over scalar variables and definetly has a special value variable
        :param key_decomp_function:
        :param scalar_vars: list of scalar variables, whose values should be abstracted
        :param dict_vars: list of dictionary variables, whose values should be abstracted
        :param scalar_k_conv: conversion function to convert from scalar domain elements to key domain elements (can be omitted, if the domains are the same)
        :param k_scalar_conv: conversion function to convert from key domain elements to scalar domain elements (can be omitted, if the domains are the same)
        :param scalar_v_conv: conversion function to convert from scalar domain elements to value domain elements (can be omitted, if the domains are the same)
        :param v_scalar_conv: conversion function to convert from value domain elements to scalar domain elements (can be omitted, if the domains are the same)
        """
        super().__init__()

        if scalar_vars is None:
            scalar_vars = []
        if dict_vars is None:
            dict_vars = []

        self._s_vars = scalar_vars
        self._d_vars = dict_vars

        self._k_domain = key_domain
        self._v_domain = value_domain

        self._s_domain = scalar_domain
        self._scalar_state = scalar_domain(scalar_vars)         #TODO: require as input?

        # special variable names:
        self._k_name = "0v_k"
        self._v_name = "0v_v"

        arguments = {}
        for dv in dict_vars:
            typ = dv.typ
            if isinstance(typ, DictLyraType):  # should be true
                if typ not in arguments:
                    if issubclass(key_domain, Store):   # not relational -> don't need scalar vars # TODO: also for op? Or only for repr?
                        key_vars = []
                    else:
                        key_vars = scalar_vars.copy()
                    if issubclass(value_domain, Store):
                        value_vars = []
                    else:
                        value_vars = scalar_vars.copy()
                    k_var = VariableIdentifier(typ.key_type, self._k_name)
                    key_vars.append(k_var)
                    v_var = VariableIdentifier(typ.value_type, self._v_name)
                    value_vars.append(v_var)

                    arguments[typ] = {'key_decomp_function': key_decomp_function, 'key_domain': key_domain, 'value_domain': value_domain,
                                    'key_d_args': {'variables':key_vars}, 'value_d_args': {'variables':value_vars}}
            else:
                raise TypeError("Dictionary variables should be of DictLyraType")

        lattices = defaultdict(lambda: DictSegmentLattice)
        self._dict_store = Store(dict_vars, lattices, arguments)

        for k in arguments.keys():
            arguments[k]['value_domain'] = BoolLattice
            del arguments[k]['value_d_args']
        self._init_store = Store(dict_vars, lattices, arguments)

        self._s_k_conv = scalar_k_conv
        self._k_s_conv = k_scalar_conv
        self._s_v_conv = scalar_v_conv
        self._v_s_conv = v_scalar_conv

    @property
    def scalar_state(self) -> Union[RelationalStore, State]:
        """Abstract state of scalar variable values."""
        return self._scalar_state

    @property
    def dict_store(self) -> Store:
        """Abstract store of dictionary variable contents."""
        return self._dict_store

    @property
    def init_store(self) -> Store:
        """Abstract store of dictionary variable initialization info."""
        return self._init_store

    def __repr__(self):
        k_is_store = issubclass(self._k_domain, Store)
        v_is_store = issubclass(self._v_domain, Store)
        if k_is_store or v_is_store:
            v_k = VariableIdentifier(LyraType(), self._k_name)  # type does not matter, because eq in terms of name
            v_v = VariableIdentifier(LyraType(), self._v_name)
            result = repr(self.scalar_state)
            for d, d_lattice in self.dict_store.store.items():
                result += f", {d} -> {{"
                first = True
                for (k, v) in d_lattice.segments:
                    if first:
                        first = False
                    else:
                        result += ", "
                    result += "("
                    if k_is_store:
                        result += repr(k.store[v_k])      # only print value of v_k
                    else:
                        result += repr(k)
                    result += ", "
                    if v_is_store:
                        result += repr(v.store[v_v])  # only print value of v_v
                    else:
                        result += repr(v)
                    result += ")"
                result += "}"

            result += ", "

            for d, i_lattice in self.init_store.store.items():
                result += f", {d} -> {{"
                first = True
                for (k, v) in i_lattice.segments:
                    if first:
                        first = False
                    else:
                        result += ", "
                    result += "("
                    if k_is_store:
                        result += repr(k.store[v_k])  # only print value of v_k
                    else:
                        result += repr(k)
                    result += ", "
                    result += repr(v)
                    result += ")"
                result += "}"
            return result
        else:
            return f"{self.scalar_state}, {self.dict_store}, {self.init_store}"

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'DictContentState':
        """The bottom lattice element is defined point-wise."""
        self.scalar_state.bottom()
        self.dict_store.bottom()
        self.init_store.bottom()
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'DictContentState':
        """The top lattice element is defined point-wise."""
        self.scalar_state.top()
        self.dict_store.top()
        self.init_store.top()
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        """The current state is bottom if `all` of its three elements are bottom"""
        return self.scalar_state.is_bottom() and self.dict_store.is_bottom() and self.init_store.is_bottom()
    # TODO: store = bottom if any element bottom -> correct?

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        """The current state is bottom if `all` of its three elements are top"""
        return self.scalar_state.is_top() and self.dict_store.is_top() and self.init_store.is_top()

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'DictContentState') -> bool:
        """Defined point-wise"""
        scaler_le = self.scalar_state.less_equal(other.scalar_state)
        dict_le = self.dict_store.less_equal(other.dict_store)
        init_le = self.init_store.less_equal(other.init_store)
        return scaler_le and dict_le and init_le

    @copy_docstring(Lattice._join)
    def _join(self, other: 'DictContentState') -> 'DictContentState':
        """Defined point-wise"""
        self.scalar_state.join(other.scalar_state)
        self.dict_store.join(other.dict_store)
        self.init_store.join(other.init_store)
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'DictContentState'):
        """Defined point-wise"""
        self.scalar_state.meet(other.scalar_state)
        self.dict_store.meet(other.dict_store)
        self.init_store.meet(other.init_store)
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'DictContentState'):
        """To avoid imprecise widening of DictSegmentLattice, first widen the scalar state"""
        old_scalar = deepcopy(self.scalar_state)
        self.scalar_state.widening(other.scalar_state)
        if old_scalar != self.scalar_state:        # TODO: comparison working?
            self.dict_store.join(other.dict_store)
            self.init_store.join(other.init_store)
        else:
            self.dict_store.widening(other.dict_store)
            self.init_store.widening(other.init_store)
        return self

    # helper
    def eval_key(self, key_expr: Expression) \
            -> Union[RelationalStore, State]: # (returns key_domain element)
        scalar_copy = deepcopy(self.scalar_state)
        v_k = VariableIdentifier(key_expr.typ, self._k_name)       # TODO: type?
        scalar_copy.add_var(v_k)# scalar_copy.variables.append() ?  # TODO: add function
        scalar_copy.assign({v_k},{key_expr})

        return self._s_k_conv(scalar_copy)

    # helper
    def eval_value(self, value_expr: Expression) \
            -> Union[RelationalStore, State]:  # (returns value_domain element)      # TODO: value expression
        scalar_copy = deepcopy(self.scalar_state)
        v_v = VariableIdentifier(value_expr.typ, self._v_name)  # TODO: type?
        scalar_copy.add_var(v_v)  # scalar_copy.variables.append() ?  # TODO: add function
        scalar_copy.assign({v_v}, {value_expr})

        return self._s_v_conv(scalar_copy)

    # helper
    def eval_value_at(self, dict: VariableIdentifier, key_abs: Union[RelationalStore, State]) \
            -> Union[RelationalStore, State]:  # (returns value_domain element)
        # returns the join of all value abstraction of segments of dictionary dict,
        #  whose key overlaps with key_abs
        if issubclass(self._v_domain, Store):
            value_vars = []
        else:
            value_vars = self._s_vars.copy()
        v_var = VariableIdentifier(dict.typ.value_type, self._v_name)
        value_vars.append(v_var)

        result = self._v_domain(variables=value_vars).bottom()       # TODO: correct?
        for (k,v) in self.dict_store.store[dict].segments:
            key_meet_s = deepcopy(key_abs).meet(k)
            if not key_meet_s.is_bottom():  # overlap/key may be contained in this segment
                result.join(v)

        return result


    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        all_ids = left.ids().union(right.ids())
        scalar_types = {BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType}# /immutable TODO: make module-global?/ put function in types?

        if all(type(id.typ) in scalar_types for id in all_ids):   # TODO: not any?

            # completely SCALAR STMT
            # update scalar part
            self.scalar_state.assign({left}, {right})

            # update relations with scalar variables
            for d_lattice in self.dict_store.store.values():
                for (k1,v) in d_lattice.segments:
                    k1.assign({left}, {right})
                    v.assign({left}, {right})
                d_lattice.d_norm_own()
            for i_lattice in self.init_store.store.values():
                for (k2,b) in i_lattice.segments:        # b must be True
                    k2.assign({left}, {right})
                i_lattice.d_norm_own()


        else:   # TODO: visitor?
            if isinstance(left, VariableIdentifier):
                if isinstance(right, Subscription):   # TODO: Slicing?
                    # DICT READ
                    if isinstance(right.key, Expression):   # TODO: expr as key?
                        k_abs = self.eval_key(right.key)
                        v_abs = self.eval_value_at(right.target, k_abs)

                        v_v = VariableIdentifier(left.typ, self._v_name)        # TODO: type?
                        self.scalar_state.add_var(v_v)
                        self.scalar_state.meet(self._v_s_conv(v_abs))
                        self.scalar_state.assign({left},{v_v})
                        self.scalar_state.remove_var(v_v)

                        # invalidate old left
                        for d_lattice in self.dict_store.store.values():
                            d_lattice.forget_var(left)
                        for i_lattice in self.init_store.store.values():
                            i_lattice.forget_var(left)
                    else:
                        raise NotImplementedError(
                            f"Assignment '{left} = {right}' is not yet supported")
                elif isinstance(right, DictDisplay):
                    # "NEW DICT"
                    left_lattice = self.dict_store.store[left]
                    left_i_lattice = self.init_store.store[left]
                    # erase all dict contents before:
                    left_lattice.bottom()
                    left_i_lattice.top()        # everything uninitialized
                    for i in range(len(right.keys)):    # similar to write
                        k_abs = self.eval_key(right.keys[i])
                        v_abs = self.eval_value(right.values[i])

                        # k_abs must be a singleton -> 'strong update'
                        left_lattice.partition_add(k_abs, v_abs)
                        left_i_lattice.partition_add(k_abs, BoolLattice(False))

                else:
                    raise NotImplementedError(
                        f"Assignment '{left} = {right}' is not yet supported")

            elif isinstance(left, Subscription):      # TODO: Slicing?
                # DICT WRITE
                if isinstance(right, Expression):        # TODO: other expr
                    if isinstance(left.key, Expression):  # TODO: expr as key?
                        k_abs = self.eval_key(left.key)
                        v_abs = self.eval_value(right)

                        v_k = VariableIdentifier(left.key.typ, self._k_name)  # TODO: type?
                        d_lattice: 'DictSegmentLattice' = self.dict_store.store[left.target]
                        if k_abs.is_singleton(v_k):       # TODO: implement (or provide predicate as arg for init
                            # STRONG UPDATE
                            d_lattice.partition_add(k_abs, v_abs)
                            i_lattice: 'DictSegmentLattice' = self.init_store.store[left.target]
                            i_lattice.partition_add(k_abs, BoolLattice(False))
                        else:
                            # WEAK UPDATE
                            # add segment & normalize
                            d_lattice.normalized_add(k_abs, v_abs)
                    else:
                        raise NotImplementedError(
                            f"Assignment '{left} = {right}' is not yet supported")
            else:
                raise NotImplementedError(f"Assignment '{left} = {right}' is not yet supported")
            # TODO: other stmts

        return self

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'DictContentState':
        # for identifier in condition.ids():
        #     if isinstance(identifier, VariableIdentifier):
        #         self.store[identifier].top()
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'DictContentState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'DictContentState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'DictContentState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'DictContentState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'DictContentState':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'DictContentState':
        raise RuntimeError("Unexpected substitute in a forward analysis!")