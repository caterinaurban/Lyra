"""
Fulara Syntactic Dictionary Usage Abstract Domain
===============================

Abstract domain to be used for **input data usage analysis** using syntactic variable dependencies
with support to analyze abstract dictionary segments.
A program variable or dictionary segment
can have value *U* (used), *S* (scoped), *W* (written), and *N* (not used).

:Authors: Lowis Engel
"""
from collections import defaultdict
from copy import deepcopy, copy
from typing import Type, Set, Union, Callable

from lyra.abstract_domains.container.fulara.fulara_domain import FularaState
from lyra.abstract_domains.container.fulara.fulara_lattice import FularaLattice
from lyra.abstract_domains.container.fulara.key_wrapper import KeyWrapper
from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.abstract_domains.usage.usage_domain import SimpleUsageStore
from lyra.abstract_domains.usage.usage_lattice import UsageLattice
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, \
    _iter_child_exprs, NegationFreeNormalExpression, Keys, Values, \
    Items
from lyra.core.types import BooleanLyraType, IntegerLyraType, StringLyraType, \
    FloatLyraType, DictLyraType
from lyra.core.utils import copy_docstring

Status = UsageLattice.Status

# special variable names:
k_name = "0v_k"

scalar_types = {BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType}


class FularaUsageLattice(Lattice):
    """Dictionary segment usage analysis state.
    An element of the dictionary segment usage abstract domain.

    It consists of the following 3 elements:
    - Usage domain state over all scalar variables, abstracting their usage status
    - Map from each dictionary variables to a DictSegmentLattice element with a given key domain K
       and the usage domain as value domain, abstracting the usage state of the dictionary segments
    - Map from each dictionary variable to a usage status for the usage of the dictionary length

    All elements are *not used* by default

    .. document private methods
    .. automethod:: FularaUsageLattice._assign
    .. automethod:: FularaUsageLattice._assume
    .. automethod:: FularaUsageLattice._output
    .. automethod:: FularaUsageLattice._substitute
    """

    # here the Union type means a logical AND: Domains should inherit from both Wrapper and State
    def __init__(self, key_domain: Type[Union[KeyWrapper, State]],
                 scalar_vars: Set[VariableIdentifier] = None,
                 dict_vars: Set[VariableIdentifier] = None):
        """Map each program variable/dictionary segment to its usage status.

        :param key_domain: domain for abstraction of dictionary keys,
            ranges over the scalar variables and the special key variable v_k
        :param scalar_vars: list of scalar variables, whose usage should be abstracted
        :param dict_vars: list of dictionary variables, whose usage should be abstracted
        """
        super().__init__()

        if scalar_vars is None:
            scalar_vars = set()
        if dict_vars is None:
            dict_vars = set()

        self._s_vars = scalar_vars
        self._d_vars = dict_vars

        self._k_domain = key_domain

        self._scalar_usage = SimpleUsageStore(scalar_vars)

        arguments = {}
        for dv in dict_vars:
            typ = dv.typ
            if isinstance(typ, DictLyraType):  # should be true
                if typ not in arguments:
                    # if issubclass(key_domain, Store):  # not relational -> don't need scalar vars
                    #     key_vars = []
                    # else:
                    # key_vars = scalar_vars.copy()
                    # if issubclass(value_domain, Store):
                    #     value_vars = []
                    # else:
                    # value_vars = scalar_vars.copy()
                    k_var = VariableIdentifier(typ.key_type, k_name)

                    arguments[typ] = {'key_domain': key_domain, 'value_domain': UsageLattice,
                                      'key_d_args': {'scalar_variables': scalar_vars,
                                                     'k_var': k_var}}
            else:
                raise TypeError("Dictionary variables should be of DictLyraType")

        lattices = defaultdict(lambda: FularaLattice)
        self._dict_usage = Store(dict_vars, lattices, arguments)
        # start with 'not used'
        for var in dict_vars:
            self._dict_usage.store[var].empty()

        # self._length_usage # TODO

    @property
    def scalar_usage(self) -> SimpleUsageStore:
        """Usage state of scalar variable values."""
        return self._scalar_usage

    @property
    def dict_usage(self) -> Store:
        """Abstract store of dictionary variable contents."""
        return self._dict_usage

    def __repr__(self):
        return f"{self.scalar_usage}, {self.dict_usage}"

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'FularaUsageLattice':
        """Point-wise"""
        self.scalar_usage.bottom()
        self.dict_usage.bottom()
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'FularaUsageLattice':
        """Point-wise"""
        self.scalar_usage.top()
        self.dict_usage.top()
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        """Point-wise"""
        scalar_b = self.scalar_usage.is_bottom()
        dict_b = self.dict_usage.is_bottom()
        return scalar_b and dict_b

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        """Point-wise"""
        scalar_t = self.scalar_usage.is_top()
        dict_t = self.dict_usage.is_top()
        return scalar_t and dict_t

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'FularaUsageLattice') -> bool:
        """Defined point-wise"""
        scalar_le = self.scalar_usage.less_equal(other.scalar_usage)
        dict_le = self.dict_usage.less_equal(other.dict_usage)
        return scalar_le and dict_le

    @copy_docstring(Lattice._join)
    def _join(self, other: 'FularaUsageLattice') -> 'FularaUsageLattice':
        """Defined point-wise"""
        self.scalar_usage.join(other.scalar_usage)
        self.dict_usage.join(other.dict_usage)
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'FularaUsageLattice'):
        """Defined point-wise"""
        self.scalar_usage.meet(other.scalar_usage)
        self.dict_usage.meet(other.dict_usage)
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'FularaUsageLattice'):
        """To avoid imprecise widening of FularaLattice, first widens the scalar state"""
        old_scalar = deepcopy(self.scalar_usage)
        self.scalar_usage.widening(other.scalar_usage)
        if old_scalar != self.scalar_usage:
            self.dict_usage.join(other.dict_usage)
        else:
            self.dict_usage.widening(other.dict_usage)
        return self

    def increase(self) -> 'FularaUsageLattice':
        """Increase the nesting level.

        :return: current lattice element modified to reflect an increased nesting level

        The increase is performed point-wise for each variable/segmetn.
        """
        self.scalar_usage.increase()

        d_store = self.dict_usage.store
        for d, d_lattice in d_store.items():
            old_segments = copy(d_lattice.segments)     # TODO: deep?
            for (k, v) in old_segments:
                d_lattice.segments.remove((k, v))
                if not v.is_written():      # don't want to add a N segment
                    v_copy: UsageLattice = copy(v)
                    v_copy.increase()
                    d_lattice.segments.add((k, v_copy))
        return self

    def decrease(self, other: 'FularaUsageLattice') -> 'FularaUsageLattice':
        """Decrease the nesting level by combining lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to reflect a decreased nesting level

        The decrease is performed point-wise for each variable/segment.
        """
        self.scalar_usage.decrease(other.scalar_usage)

        # weak update (could be strong for singletons + better partitioning)
        self.dict_usage.join(other.dict_usage)      # TODO: correct?

        # self_d_store = self.dict_usage.store
        # other_d_store = other.dict_usage.store
        # for d in self_d_store.keys():        # should have the same dict_variables
        #     self_lattice: FularaLattice = self_d_store[d]
        #     other_lattice: FularaLattice = other_d_store[d]
        #     self_segments = self_lattice.sorted_segments()      # TODO: deepcopy?
        #     other_segments = other_lattice.sorted_segments()
        #     result_segments = set()
        #     for (k_s, v_s) in self_segments:
        #         # k_partitions = []
        #         # partition_segments = set()
        #         next_start = 0
        #         self_lattice.segments.remove((k_s, v_s))
        #         v_new = deepcopy(v_s)       # copy to avoid modifying tuple
        #         for i, (k_o, v_o) in enumerate(other_segments):
        #             if k_s < k_o:   # => k_s not overlapping with k_o
        #                 # => other = N at that point => keep self_segment
        #                 break   # proceed in self_segments
        #             elif k_o < k_s:
        #                 next_start = i + 1       # don't need to look at it again
        #                 continue    # proceed in other_segments
        #             elif k_s == k_o:
        #                 if v_s != v_o and (v_o.is_top() or v_o.is_written()):
        #                     # replace by other segment
        #                     v_new = v_o
        #                     # self_lattice.segments.remove((k_s, v_s))
        #                     # self_lattice.segments.add((k_o, v_o))
        #                 next_start = i + 1  # don't need to look at it again
        #                 break   # proceed in self_segments
        #             else:   # segments overlap (?) check meet?
        #                 if v_s != v_o and (v_o.is_top() or v_o.is_written()):
        #                     # weak update without partitioning:
        #                     v_new.join(deepcopy(v_o))
        #                 # # partitioning:       # TODO: weak update with partitioning
        #                 # overlap = deepcopy(k_s).meet(deepcopy(k_o))
        #                 # k_partitions.append(overlap)
        #                 # if v_s != v_o and (v_o.is_top() or v_o.is_written()):
        #                 #     # weak update
        #                 #     v_join = deepcopy(v_s).join(deepcopy(v_o))
        #                 #     partition_segments.add((overlap, v_join))
        #                 # else: # no update, just partition
        #                 #     partition_segments.add((overlap, v_s))
        #
        #         # if k_partitions:    # non-empty
        #         #     assert()
        #
        #
        #         other_segments = other_segments[next_start:]
        return self


class FularaUsageState(Stack, State):
    """Input data usage analysis state.     # TODO: doc
    An element of the syntactic usage abstract domain.

    Stack of maps from each program variable to its usage status.
    The stack contains a single map by default.

    .. note:: Program variables storing lists are abstracted via summarization.

    .. document private methods
    .. automethod:: SimpleUsageState._assign
    .. automethod:: SimpleUsageState._assume
    .. automethod:: SimpleUsageState._output
    .. automethod:: SimpleUsageState._substitute
    """

    def __init__(self, key_domain: Type[KeyWrapper],
                 scalar_vars: Set[VariableIdentifier] = None,
                 dict_vars: Set[VariableIdentifier] = None,
                 k_k_pre_conv: Callable[[KeyWrapper], KeyWrapper]
                 = lambda x: x,
                 k_pre_k_conv: Callable[[KeyWrapper], KeyWrapper]
                 = lambda x: x,
                 precursory: FularaState = None):
        arguments = {'key_domain': key_domain, 'scalar_vars': scalar_vars, 'dict_vars': dict_vars}
        super().__init__(FularaUsageLattice, arguments)    # Stack
        State.__init__(self, precursory)

        # self._s_vars = scalar_vars
        self._k_k_pre_conv = k_k_pre_conv
        self._k_pre_k_conv = k_pre_k_conv

        # self._loop_flag = False

    # @property
    # def scalar_vars(self) -> Set[VariableIdentifier]:
    #     return self._s_vars

    # TODO: properties?
    @copy_docstring(Stack.push)
    def push(self):
        if self.is_bottom() or self.is_top():
            return self
        self.stack.append(deepcopy(self.lattice).increase())
        return self

    @copy_docstring(Stack.pop)
    def pop(self):
        if self.is_bottom() or self.is_top():
            return self
        current = self.stack.pop()
        self.lattice.decrease(current)
        return self

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    # helper:
    def make_used(self, expression: Expression):        # TODO: or use recursion?
        """makes all variables / dictionary segment accessed in expr used"""

        def own_walk(e: Expression):
            """
            Recursively yield all expressions in an expression tree
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
                elif isinstance(e, (Keys, Values, Items)):
                    pass
                else:
                    todo.extend(_iter_child_exprs(e))
                yield e

        for expr in own_walk(expression):
            if isinstance(expr, VariableIdentifier):
                if type(expr.typ) in scalar_types:
                    self.lattice.scalar_usage.store[expr].top()
                    # update dictionary usage at corresponding position
                    # if variable occured in a 'in-condition'
                    # only track value usage
                    for (d_var, k_var, v_var) in self.precursory.in_relations.find_value(expr):
                        d_lattice: FularaLattice = self.lattice.dict_usage.store[d_var]
                        if k_var is None:   # Values condition
                            v_abs = self.precursory.eval_value(v_var)
                            old_segments = copy(d_lattice.segments)
                            for (k, v) in old_segments:
                                value_meet_v = deepcopy(v_abs).meet(v)
                                if not value_meet_v.is_bottom():  # value may be in this segment
                                    # mark segment as used
                                    if not v.is_top():
                                        d_lattice.segments.remove((k, v))
                                        d_lattice.segments.add((k, UsageLattice(Status.U)))
                        else:      # Items condition
                            k_pre = self.precursory.eval_key(k_var)     # may be refined
                            k_abs = self._k_pre_k_conv(k_pre)
                            # weak update = strong update, since U is top
                            d_lattice.partition_add(k_abs, UsageLattice(Status.U))

                elif isinstance(expr.typ, DictLyraType):
                    self.lattice.dict_usage.store[expr].top()
                else:
                    raise NotImplementedError(
                        f"Type '{expr.typ}' of variable {expr} not supported")
            elif isinstance(expr, Subscription) and isinstance(expr.target.typ, DictLyraType):
                d_lattice: FularaLattice = self.lattice.dict_usage.store[expr.target]
                pre_copy: FularaState = deepcopy(self.precursory)  # TODO: copy needed?
                scalar_key = pre_copy._read_eval.visit(expr.key)
                k_pre = pre_copy.eval_key(scalar_key)
                k_abs = self._k_pre_k_conv(k_pre)
                # weak update = strong update, since U is top
                d_lattice.partition_add(k_abs, UsageLattice(Status.U))
            elif isinstance(expr, (Keys, Values, Items)):
                # TODO: length usage
                pass       # value usage done inside loop/branch by using InRelations

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'FularaUsageState':
        condition = NegationFreeNormalExpression().visit(condition)     # eliminate negations

        # if self._loop_flag:     # TODO: not really working
        #     if isinstance(condition, BinaryComparisonOperation):
        #         if condition.operator == BinaryComparisonOperation.Operator.In:
        #             left = condition.left
        #             if isinstance(left, VariableIdentifier) and type(left.typ) in scalar_types:
        #                 left_state = self.lattice.scalar_usage.store[left]
        #                 # loop condition -> like assignment left := right
        #                 if left_state.is_scoped() or left_state.is_top():
        #                     left_state.written()
        #                     self.make_used(condition.right)
        #                 return self
        #             elif isinstance(left, TupleDisplay) \
        #                 and all(type(i.typ) in scalar_types for i in left.items):
        #                 # loop condition -> like assignment left := right
        #                 left_u_s = False
        #                 for i in left.items:
        #                     i_state = self.lattice.scalar_usage.store[i]
        #                     if i_state.is_scoped() or i_state.is_top():
        #                         i_state.written()
        #                         left_u_s = True
        #                 if left_u_s:
        #                     self.make_used(condition.right)
        #                 return self
        #             else:
        #                 error = f"The loop condition {condition} is not yet supported!"
        #                 raise NotImplementedError(error)
        #         # TODO: not in?
        #         elif condition.operator == BinaryComparisonOperation.Operator.NotIn:
        #             return self     # do nothing
        #             # left = condition.left
        #             # if isinstance(left, VariableIdentifier) and type(left.typ) in scalar_types:
        #             #     self.make_used(condition.right)
        #             #     return self
        #             # else:
        #             #     error = f"The loop condition {condition} is not yet supported!"
        #             #     raise NotImplementedError(error)

        # default:
        effect = False  # effect of the current nesting level on the outcome of the program
        for variable in self.lattice.scalar_usage.variables:
            value = self.lattice.scalar_usage.store[variable]
            if value.is_written() or value.is_top():
                effect = True
                break
        else:   # no scalar variable effected
            d_store = self.lattice.dict_usage.store
            for d, d_lattice in d_store.items():
                for (_, v) in d_lattice.segments:
                    if v.is_written() or v.is_top():
                        effect = True
                        break
                else:
                    continue
                break

        if effect:  # the current nesting level has an effect on the outcome of the program
            self.make_used(condition)

        # TODO: update key domain relations
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'FularaUsageState':
        return self.push()

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'FularaUsageState':
        return self.pop()

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'FularaUsageState':
        return self.push()

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'FularaUsageState':
        return self.pop()

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'FularaUsageState':
        self.make_used(output)
        return self

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'FularaUsageState':
        left_u_s = False    # left expression is used or scoped
        if isinstance(left, VariableIdentifier):
            if type(left.typ) in scalar_types:
                left_state = self.lattice.scalar_usage.store[left]
                if left_state.is_top() or left_state.is_scoped():
                    left_u_s = True
                    left_state.written()      # left overwritten
            elif isinstance(left.typ, DictLyraType):
                left_lattice: FularaLattice = self.lattice.dict_usage.store[left]
                left_u_s = any(v.is_top() or v.is_scoped() for (_, v) in left_lattice.segments)

                # U/W/S segments (all) -> overwritten (W) (if any):
                old_segments = copy(left_lattice.segments)
                left_lattice.segments.clear()
                for (k, v) in old_segments:
                    left_lattice.segments.add((k, UsageLattice(Status.W)))
            else:
                error = f"Substitution for {left} is not yet implemented!"
                raise NotImplementedError(error)
        elif isinstance(left, Subscription) and isinstance(left.target.typ, DictLyraType):
            left_lattice: FularaLattice = self.lattice.dict_usage.store[left.target]
            pre_copy: FularaState = deepcopy(self.precursory)  # TODO: copy needed?
            scalar_key = pre_copy._read_eval.visit(left.key)
            k_pre = pre_copy.eval_key(scalar_key)
            k_abs = self._k_pre_k_conv(k_pre)

            old_segments = copy(left_lattice.segments)
            if k_abs.is_singleton():    # strong update -> W (if U/S)
                for (k, v) in old_segments:
                    key_meet_k = deepcopy(k_abs).meet(k)
                    if not key_meet_k.is_bottom():    # key may be contained in this segment
                        if v.is_top() or v.is_scoped():  # TODO: more efficient way?
                            left_u_s = True
                            left_lattice.partition_add(k_abs, UsageLattice(Status.W))   # strong update
                    break   # there can only be one overlapping segment (since k_abs is singleton)
            else:
                for (k, v) in old_segments:
                    key_meet_k = deepcopy(k_abs).meet(k)
                    if not key_meet_k.is_bottom():  # key may be contained in this segment
                        if v.is_top():
                            left_u_s = True
                            # no need to change usage (since weak update and W join U = U)
                        elif v.is_scoped():
                            left_u_s = True
                            left_lattice.segments.remove((k, v))
                            # weak update: W join S = U     # TODO: only update overlapping parts?
                            left_lattice.segments.add((k, UsageLattice(Status.U)))

            if left_u_s:      # make subscript used
                self.make_used(left.key)

        else:
            error = f"Substitution for {left} is not yet implemented!"
            raise NotImplementedError(error)

        if left_u_s:        # left is used or scoped -> right is used
            self.make_used(right)

        return self
