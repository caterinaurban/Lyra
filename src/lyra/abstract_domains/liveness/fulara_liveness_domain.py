"""
Fulara Dictionary Strongly Live Abstract Domain
===============================

Abstract domain to be used for **strongly live analysis**.
A program variable or dictionary segment is *strongly live* if
it is used in an assignment to another strongly live variable or dictionary segment,
or if is used in a statement other than an assignment.

:Authors: Lowis Engel
"""
from collections import defaultdict
from copy import deepcopy, copy
from typing import Type, Set, Callable

from lyra.abstract_domains.container.fulara.fulara_domain import FularaState
from lyra.abstract_domains.container.fulara.fulara_lattice import FularaLattice
from lyra.abstract_domains.container.fulara.key_wrapper import KeyWrapper
from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.liveness.liveness_domain import LivenessLattice, StrongLivenessState
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, \
    _iter_child_exprs, Keys, Values, \
    Items
from lyra.core.types import BooleanLyraType, IntegerLyraType, StringLyraType, \
    FloatLyraType, DictLyraType, ListLyraType
from lyra.core.utils import copy_docstring

Status = LivenessLattice.Status

# special variable names:
k_name = "0v_k"

scalar_types = {BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType}
map_types = {DictLyraType, ListLyraType}


class FularaLivenessState(State):
    """Fulara strongly liveness analysis state.
    An element of the Fulara strongly live abstract domain.

    It consists of the following 2 elements:
    - Strongly Liveness domain state over all scalar variables, abstracting their liveness status
    - Map from each dictionary variable to a DictSegmentLattice element with a given key domain K
       and the liveness domain as value domain,
       abstracting the liveness state of the dictionary segments
    TODO: Map from each dictionary variable to a live status for the usage of the dictionary length

    All elements are *dead*(bottom) by default.

    .. document private methods
    .. automethod:: FularaLivenessState._assign
    .. automethod:: FularaLivenessState._assume
    .. automethod:: FularaLivenessState._output
    .. automethod:: FularaLivenessState._substitute
    """

    def __init__(self, key_domain: Type[KeyWrapper],
                 precursory: FularaState,
                 scalar_vars: Set[VariableIdentifier] = None,
                 map_vars: Set[VariableIdentifier] = None,
                 k_pre_k_conv: Callable[[KeyWrapper], KeyWrapper]
                 = lambda x: x):
        """Map each program variable/dictionary segment to its liveness status.
        :param key_domain: domain for abstraction of dictionary keys,
            ranges over the scalar variables and the special key variable v_k,
            should support backward assignments with _substitute
        :param precursory: Forward analysis (Fulara analysis) result above the current statement
        :param scalar_vars: list of scalar variables, whose liveness should be abstracted
        :param map_vars: list of map variables, whose usage should be abstracted
        :param k_pre_k_conv: Conversion function to convert from key domain elements of the
                             precursory analysis to key domain elements of this analysis
                             (if the domains differ)
        """

        super().__init__(precursory)

        self._s_vars = scalar_vars or set()
        self._m_vars = map_vars or set()

        self._k_domain = key_domain

        self._scalar_liveness = StrongLivenessState(scalar_vars)

        arguments = {}
        for dv in map_vars:
            typ = dv.typ
            if isinstance(typ, DictLyraType):
                k_var = VariableIdentifier(typ.key_typ, k_name)
            elif isinstance(typ, ListLyraType):
                k_var = VariableIdentifier(IntegerLyraType(), k_name)
            else:
                raise TypeError("Map variables should be of type DictLyraType or ListLyraType")

            if typ not in arguments:
                arguments[typ] = {'key_domain': key_domain, 'value_domain': LivenessLattice,
                                  'key_d_args': {'scalar_variables': scalar_vars, 'k_var': k_var}}

        lattices = defaultdict(lambda: FularaLattice)
        self._dict_liveness = Store(map_vars, lattices, arguments)
        # start with 'dead'
        for var in map_vars:
            self._dict_liveness.store[var].empty()

        # self._length_usage # TODO

        self._k_pre_k_conv = k_pre_k_conv

    @property
    def scalar_liveness(self) -> StrongLivenessState:
        """Liveness state of scalar variable values."""
        return self._scalar_liveness

    @property
    def dict_liveness(self) -> Store:
        """Abstract store of dictionary variable liveness information."""
        return self._dict_liveness

    @property
    def k_pre_k_conv(self):
        return self._k_pre_k_conv

    def __repr__(self):
        return f"{self.scalar_liveness}, {self.dict_liveness}"

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'FularaLivenessState':
        """Point-wise, setting all elements to 'Dead'"""
        self.scalar_liveness.bottom()
        for d_lattice in self.dict_liveness.store.values():
            d_lattice.empty()
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'FularaLivenessState':
        """Point-wise"""
        self.scalar_liveness.top()
        self.dict_liveness.top()
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        """Point-wise, `all` elements map to 'Dead'"""
        scalar_b = self.scalar_liveness.is_bottom()
        dict_b = all(d_lattice.is_empty() for d_lattice in self.dict_liveness.store.values())
        return scalar_b and dict_b

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        """Point-wise"""
        scalar_t = self.scalar_liveness.is_top()
        dict_t = self.dict_liveness.is_top()
        return scalar_t and dict_t

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'FularaLivenessState') -> bool:
        """Defined point-wise"""
        scalar_le = self.scalar_liveness.less_equal(other.scalar_liveness)
        dict_le = self.dict_liveness.less_equal(other.dict_liveness)
        return scalar_le and dict_le

    @copy_docstring(Lattice._join)
    def _join(self, other: 'FularaLivenessState') -> 'FularaLivenessState':
        """Defined point-wise"""
        self.scalar_liveness.join(other.scalar_liveness)
        self.dict_liveness.join(other.dict_liveness)
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'FularaLivenessState'):
        """Defined point-wise"""
        self.scalar_liveness.meet(other.scalar_liveness)
        self.dict_liveness.meet(other.dict_liveness)
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'FularaLivenessState'):
        """To avoid imprecise widening of FularaLattice, first widens the scalar state"""
        old_scalar = deepcopy(self.scalar_liveness)
        self.scalar_liveness.widening(other.scalar_liveness)
        if old_scalar != self.scalar_liveness:
            self.dict_liveness.join(other.dict_liveness)
        else:
            self.dict_liveness.widening(other.dict_liveness)
        return self

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    # helper:
    def make_live(self, expression: Expression):        # TODO: or use recursion?
        """makes all variables / dictionary segments accessed in expr live"""

        def own_walk(e: Expression):
            """
            Recursively yield all expressions in an expression tree that we want to make live
            starting at ``expr`` (including ``expr`` itself),
            in no specified order.

            adapted from _walk in expressions.py
            """
            from collections import deque
            todo = deque([e])
            while todo:
                e = todo.popleft()
                if isinstance(e, Subscription):  # don't look at dictionary var
                    # still look at vars in subscript -> make them used
                    todo.extend(_iter_child_exprs(e.key))
                elif isinstance(e, Keys):
                    pass       # don't look at subexpressions
                elif isinstance(e, (Values, Items)):
                    # make the whole dictionary live, since there is always a corresponding
                    # 'NotIn'-condition which uses all values (TODO: only use initialized values?)
                    todo.extend(_iter_child_exprs(e.target_dict))
                else:
                    todo.extend(_iter_child_exprs(e))
                yield e

        for expr in own_walk(expression):
            if isinstance(expr, VariableIdentifier):
                if type(expr.typ) in scalar_types:
                    self.scalar_liveness.store[expr].top()
                    # update dictionary liveness at corresponding position
                    # if variable occurred in a 'in-condition'
                    # only track value usage
                    for (d_var, k_var, v_var) in self.precursory.in_relations.find_value(expr):
                        live_lattice: FularaLattice = self.dict_liveness.store[d_var]
                        if k_var is None:   # Values condition
                            v_abs = self.precursory.eval_value(expr)
                            # determine possible keys for this v_abs
                            pre_lattice: FularaLattice = self.precursory.dict_store.store[d_var]
                            for (k, v) in pre_lattice.segments:
                                value_meet_v = deepcopy(v_abs).meet(v)
                                if not value_meet_v.is_bottom():
                                    # value may be in this segment
                                    # mark segment as live
                                    # weak update = strong update (since setting to top)
                                    live_lattice.partition_add(k, LivenessLattice(Status.Live))
                        else:      # Items condition
                            k_pre = self.precursory.eval_key(k_var)  # may be refined by precursory
                            k_abs = self.k_pre_k_conv(k_pre)
                            # weak update = strong update (since setting to top)
                            live_lattice.partition_add(k_abs, LivenessLattice(Status.Live))

                elif type(expr.typ) in map_types:
                    self.dict_liveness.store[expr].top()
                else:
                    raise NotImplementedError(
                        f"Type '{expr.typ}' of variable {expr} not supported")
            elif isinstance(expr, Subscription) and type(expr.target.typ) in map_types:
                live_lattice: FularaLattice = self.dict_liveness.store[expr.target]
                pre_copy: FularaState = deepcopy(self.precursory)  # TODO: copy needed?
                scalar_key = pre_copy.read_eval.visit(expr.key)
                k_pre = pre_copy.eval_key(scalar_key)
                k_abs = self.k_pre_k_conv(k_pre)
                # weak update = strong update (since setting to top)
                live_lattice.partition_add(k_abs, LivenessLattice(Status.Live))
            elif isinstance(expr, (Keys, Values, Items)):
                # TODO: length usage
                pass

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'FularaLivenessState':
        self.make_live(condition)

        # update key relations (adapted from fulara_domain._assign):
        all_ids = condition.ids()
        if all(type(ident.typ) in scalar_types for ident in all_ids):
            # update relations with scalar variables in dict stores
            for d_lattice in self.dict_liveness.store.values():
                for (k, v) in d_lattice.segments:
                    d_lattice.segments.remove((k, v))  # needed, because tuple is immutable?
                    k.assume({condition})
                    d_lattice.segments.add((k, v))
                d_lattice.d_norm_own()
        else:
            self.precursory.update_dict_from_scalar(self.dict_liveness, False)
        # TODO: other cases
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'FularaLivenessState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'FularaLivenessState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'FularaLivenessState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'FularaLivenessState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'FularaLivenessState':
        self.make_live(output)
        return self

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'FularaLivenessState':
        left_live = False    # flag for left expression is live
        if isinstance(left, VariableIdentifier):
            if type(left.typ) in scalar_types:
                left_state: LivenessLattice = self.scalar_liveness.store[left]
                if left_state.is_top():
                    left_live = True
                    left_state.bottom()     # dead
            elif type(left.typ) in map_types:
                left_lattice: FularaLattice = self.dict_liveness.store[left]
                left_live = any(v.is_top() for (_, v) in left_lattice.segments)

                # whole dictionary dead
                left_lattice.bottom()
            else:
                error = f"Substitution for {left} is not yet implemented!"
                raise NotImplementedError(error)
        elif isinstance(left, Subscription) and type(left.target.typ) in map_types:
            left_lattice: FularaLattice = self.dict_liveness.store[left.target]
            pre_copy: FularaState = deepcopy(self.precursory)  # TODO: copy needed?
            scalar_key = pre_copy.read_eval.visit(left.key)
            k_pre = pre_copy.eval_key(scalar_key)
            k_abs = self.k_pre_k_conv(k_pre)

            old_segments = copy(left_lattice.segments)
            if k_abs.is_singleton():    # strong update -> dead (if live)
                for (k, v) in old_segments:
                    key_meet_k = deepcopy(k_abs).meet(k)
                    if not key_meet_k.is_bottom():    # key may be contained in this segment
                        if v.is_top():
                            left_live = True
                            # strong update:
                            left_lattice.partition_add(k_abs, LivenessLattice())
                        # there can only be one overlapping segment (since k_abs is singleton)
                        break
            else:   # weak update
                for (k, v) in old_segments:
                    key_meet_k = deepcopy(k_abs).meet(k)
                    if not key_meet_k.is_bottom():  # key may be contained in this segment
                        if v.is_top():
                            left_live = True
                            # no need to change liveness
                            # (since weak update and dead join live = live)
                            break   # nothing more to be done

            if left_live:      # make subscript live
                self.make_live(left.key)
        else:
            error = f"Substitution for {left} is not yet implemented!"
            raise NotImplementedError(error)

        if left_live:        # left is strongly live -> right is strongly live
            self.make_live(right)

        # update key relations (adapted from fulara_domain._assign):
        all_ids = left.ids().union(right.ids())
        if all(type(ident.typ) in scalar_types for ident in all_ids):
            # update relations with scalar variables in dict stores
            for d_lattice in self.dict_liveness.store.values():
                for (k, v) in d_lattice.segments:
                    d_lattice.segments.remove((k, v))  # needed, because tuple is immutable?
                    k.substitute({left}, {right})
                    d_lattice.segments.add((k, v))
                d_lattice.d_norm_own()

        elif isinstance(left, VariableIdentifier):
            if type(left.typ) in scalar_types:  # assignment to scalar variable
                # TODO: temp cleanup
                self.precursory.update_dict_from_scalar(self.dict_liveness, False)

        return self
