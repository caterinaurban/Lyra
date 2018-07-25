"""
Dictionary Content Abstract Domain
========================

Generic abstract domain to abstract scalar variables and dictionary contents.
Dictionaries are abstracted by a set of abstract segments.

:Authors: Lowis Engel
"""

from collections import defaultdict
from copy import deepcopy, copy
from typing import Tuple, Set, Type, Callable, Dict, Union, Iterator

from lyra.abstract_domains.data_structures.dict_segment_lattice import DictSegmentLattice
from lyra.abstract_domains.data_structures.key_wrapper import KeyWrapper
from lyra.abstract_domains.data_structures.scalar_wrapper import ScalarWrapper
from lyra.abstract_domains.data_structures.value_wrapper import ValueWrapper
from lyra.abstract_domains.lattice import Lattice, BottomMixin
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, Subscription, DictDisplay, \
    BinaryComparisonOperation, Keys, Items, Values, TupleDisplay, ExpressionVisitor, \
    NegationFreeNormalExpression
from lyra.core.types import DictLyraType, LyraType, BooleanLyraType, IntegerLyraType, \
    FloatLyraType, StringLyraType
from lyra.core.utils import copy_docstring

# special variable names:
k_name = "0v_k"
v_name = "0v_v"


scalar_types = {BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType}


class InRelationState(State, BottomMixin):
    """'In' lattice element
    i.e. a set of 3-tuples, covering the in-relationship between variables
    and the corresponding dictionary and between the variables introduced by loop or if conditions
    The tuples consist of a dictionary variable, a key variable and a value variable,
    where either the key or value variable can possibly be None.

    (dict, key, value), (dict, key, None), (dict, None, value)

    The default element is the empty set (top)

    .. document private methods
    .. automethod:: InRelationState._less_equal
    .. automethod:: InRelationState._meet
    .. automethod:: InRelationState._join
    .. automethod:: InRelationState._widening
    """
    def __init__(self, tuple_set:
                 Set[Tuple[VariableIdentifier, VariableIdentifier, VariableIdentifier]] = None):
        super().__init__()
        if tuple_set is None:
            tuple_set = set()
        self._tuple_set = tuple_set

    @property
    def tuple_set(self):
        """Current tuple set."""
        if self.is_bottom():
            return set()

        return self._tuple_set

    def __repr__(self):         # TODO: use join?
        if self.is_bottom():
            return "⊥"

        result = "{"
        first = True
        # output tuples sorted by their variable names
        for t in sorted(self.tuple_set,
                        key=lambda t: (t[0].name, t[1] and t[1].name, t[2] and t[2].name)):
            if first:
                result += f"({t[0]}, {t[1]}, {t[2]})"
                first = False
            else:
                result += f", ({t[0]}, {t[1]}, {t[2]})"
        result += "}"
        return result

    @copy_docstring(Lattice.top)
    def top(self):
        """The top lattice element is ``{}``."""
        self._replace(InRelationState())
        return self

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self.tuple_set == set()

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'InRelationState') -> bool:
        """An element is less_equal another,
        if its tuple set is a superset of the tuple set of the other"""
        return self.tuple_set.issuperset(other.tuple_set)

    @copy_docstring(Lattice._join)
    def _join(self, other: 'InRelationState') -> 'InRelationState':
        """Intersection of the tuple sets"""
        new_set = self.tuple_set.intersection(other.tuple_set)      # TODO: update?
        return self._replace(InRelationState(new_set))

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'InRelationState') -> 'InRelationState':
        """Union of the tuple sets"""
        new_set = self.tuple_set.union(other.tuple_set)
        return self._replace(InRelationState(new_set))

    # helpers
    def find_key(self, k: VariableIdentifier) \
            -> Iterator[Tuple[VariableIdentifier, VariableIdentifier, VariableIdentifier]]:
        """Returns the tuples from the set that have k at the key position"""
        if self.is_bottom():
            return iter(())  # empty iterator

        return filter(lambda t: (t[1] and t[1] == k), self.tuple_set)

    def find_value(self, v: VariableIdentifier) \
            -> Iterator[Tuple[VariableIdentifier, VariableIdentifier, VariableIdentifier]]:
        """Returns the tuples from the set that have v at the value position"""
        if self.is_bottom():
            return iter(())  # empty iterator

        return filter(lambda t: (t[2] and t[2] == v), self.tuple_set)

    def find_var(self, v: VariableIdentifier) \
            -> Iterator[Tuple[VariableIdentifier, VariableIdentifier, VariableIdentifier]]:
        """Returns the tuples from the set that have v at the dict OR key OR value position"""
        if self.is_bottom():
            return iter(())     # empty iterator

        return filter(lambda t: (t[0] == v) or (t[1] and t[1] == v) or (t[2] and t[2] == v),
                      self.tuple_set)

    def loop_vars(self) -> Set[VariableIdentifier]:
        """Returns the set of all key/value variables"""
        if self.is_bottom():
            return set()

        result = set()
        for t in self.tuple_set:
            result.add(t[1])
            result.add(t[2])
        return result

    def k_v_tuples(self) \
            -> Iterator[Tuple[VariableIdentifier, VariableIdentifier, VariableIdentifier]]:
        """Returns all tuples without a None (i.e. with a key & a value variable)"""
        if self.is_bottom():
            return iter(())     # empty iterator

        return filter(lambda t: (t[1] is not None) and (t[2] is not None), self.tuple_set)

    def invalidate_var(self, v: VariableIdentifier):
        """Removes v from its tuple(s)"""
        if self.is_bottom():
            return

        for v_tuple in self.find_var(v):
            self.tuple_set.remove(v_tuple)

            if (v != v_tuple[0]) and (v_tuple[1] is not None) and (v_tuple[2] is not None):
                # must keep relationship with other variable
                if v_tuple[1] == v:
                    new_tuple = (v_tuple[0], None, v_tuple[2])
                else:  # left_tuple[2] == v
                    new_tuple = (v_tuple[0], v_tuple[1], None)
                self.tuple_set.add(new_tuple)

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'InRelationState') -> 'InRelationState':
        # only finitely many variable combinations -> widening not needed?
        return self._join(other)

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        if self.is_bottom():
            return self

        if isinstance(left, VariableIdentifier):
            # invalidate left, since overwritten
            self.invalidate_var(left)

            # copy tuples of 'right'
            if isinstance(right, VariableIdentifier):    # TODO: are there other relevant cases?
                new_tuples = set()
                for right_tuple in self.find_var(right):
                    if right_tuple[0] == right:
                        new_tuples.add((left, right_tuple[1], right_tuple[2]))
                    elif right_tuple[1] and right_tuple[1] == right:
                        new_tuples.add((right_tuple[0], left, right_tuple[2]))
                    else:  # right_tuple[2] == right
                        new_tuples.add((right_tuple[0], right_tuple[1], left))

                self.tuple_set.update(new_tuples)

        return self

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'InRelationState':
        if self.is_bottom():
            return self

        if isinstance(condition, BinaryComparisonOperation):  # TODO: boolean conjunctions of them?
            if condition.operator == 9:  # op 9 == In
                if isinstance(condition.left, VariableIdentifier):
                    # TODO: don't invalidate for ifs?
                    self.invalidate_var(condition.left)

                    if isinstance(condition.right, Keys):
                        new_tuple = (condition.right.target_dict, condition.left, None)
                        self.tuple_set.add(new_tuple)
                    elif isinstance(condition.right, Values):
                        new_tuple = (condition.right.target_dict, None, condition.left)
                        self.tuple_set.add(new_tuple)
                elif isinstance(condition.left, TupleDisplay) \
                        and isinstance(condition.right, Items):
                    # TODO: don't invalidate for ifs?
                    self.invalidate_var(condition.left.items[0])
                    self.invalidate_var(condition.left.items[1])

                    left_items = condition.left.items
                    new_tuple = (condition.right.target_dict, left_items[0], left_items[1])
                    self.tuple_set.add(new_tuple)
            elif condition.operator == 10:       # NotIn
                if isinstance(condition.left, VariableIdentifier):
                    self.invalidate_var(condition.left)
                elif isinstance(condition.left, TupleDisplay) \
                        and isinstance(condition.right, Items):
                    self.invalidate_var(condition.left.items[0])
                    self.invalidate_var(condition.left.items[1])

        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'InRelationState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'InRelationState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'InRelationState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'InRelationState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'InRelationState':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'InRelationState':
        raise RuntimeError("Unexpected substitute in a forward analysis!")


class BoolLattice(Lattice):
    """Boolean lattice element (True/False),
        where True overapproximates concrete True values
        (so True -> may be True in the concrete

    (Maybe) True
          |
        False

    The default element is True (top)

    .. document private methods
    .. automethod:: BoolLattice._less_equal
    .. automethod:: BoolLattice._meet
    .. automethod:: BoolLattice._join
    .. automethod:: BoolLattice._widening
    """
    def __init__(self, value: bool = True):
        super().__init__()
        self._value = value

    @property
    def value(self):
        """Current boolean value."""
        return self._value

    def __repr__(self):
        return repr(self.value)

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        """The bottom lattice element is ``False``."""
        self._replace(BoolLattice(False))
        return self

    @copy_docstring(Lattice.top)
    def top(self):
        """The top lattice element is ``True``."""
        self._replace(BoolLattice())
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return not self._value

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return self._value

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'BoolLattice') -> bool:
        pass    # already handled by less_equal

    @copy_docstring(Lattice._join)
    def _join(self, other: 'BoolLattice') -> 'BoolLattice':
        pass    # already handled by join

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'BoolLattice') -> 'BoolLattice':
        pass    # already handled by meet

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'BoolLattice') -> 'BoolLattice':
        pass    # already handled by widening

    def invalidate_var(self, var: VariableIdentifier):
        pass    # no variables stored


class DictContentState(State):
    """Dictionary content analysis state.
    An element of the dictionary content abstract domain.

    It consists of the following 4 elements:
    - Abstract state from a given domain A over all scalar variables,
        abstracting their values
    - Map from each dictionary variables to a DictSegmentLattice-element with a given key domain K
        and value domain V, abstracting the contents of the dictionaries
    - Map from each dictionary variables to a DictSegmentLattice-element with a given key domain K
        and the BoolLattice as value domain,
        abstracting the initialization info of the dictionary elements
        (True = may be uninitialized, False/Not present = definitely initialized)
    - Relational InRelationState to cover relations between variables and dictionaries
        introduced by 'in' conditions

    Everything is Top by default

    .. document private methods
    .. automethod:: DictContentState._assign
    .. automethod:: DictContentState._assume
    .. automethod:: DictContentState._output
    .. automethod:: DictContentState._substitute
    .. automethod:: DictContentState._temp_cleanup
    .. automethod:: DictContentState._update_dict_from_refined_scalar
    """

    # here the Union type means a logical AND: Domains should inherit from both Wrapper and State
    def __init__(self, scalar_domain: Type[Union[ScalarWrapper, State]],
                 key_domain: Type[Union[KeyWrapper, State]],
                 value_domain: Type[Union[ScalarWrapper, State]],
                 scalar_vars: Set[VariableIdentifier] = None,
                 dict_vars: Set[VariableIdentifier] = None,
                 scalar_k_conv: Callable[[Union[ScalarWrapper, State]], Union[KeyWrapper, State]]
                 = lambda x: x,
                 k_scalar_conv: Callable[[Union[KeyWrapper, State]], Union[ScalarWrapper, State]]
                 = lambda x: x,
                 scalar_v_conv: Callable[[Union[ScalarWrapper, State]], Union[ValueWrapper, State]]
                 = lambda x: x,
                 v_scalar_conv: Callable[[Union[ValueWrapper, State]], Union[ScalarWrapper, State]]
                 = lambda x: x):
        """
        :param scalar_domain: domain for abstraction of scalar variable values,
            ranges over the scalar variables
            (may have different abstract domains for different types)
        :param key_domain: domain for abstraction of dictionary keys,
            ranges over the scalar variables and the special key variable v_k
        :param value_domain: domain for abstraction of dictionary values,
            ranges over the scalar variables and the special value variable v_v
        :param scalar_vars: list of scalar variables, whose values should be abstracted
        :param dict_vars: list of dictionary variables, whose values should be abstracted
        :param scalar_k_conv: conversion function to convert from scalar domain elements
                                                             to key domain elements
        :param k_scalar_conv: conversion function to convert from key domain elements
                                                             to scalar domain elements
        :param scalar_v_conv: conversion function to convert from scalar domain elements
                                                             to value domain elements
        :param v_scalar_conv: conversion function to convert from value domain elements
                                                             to scalar domain elements
        """
        super().__init__()

        if scalar_vars is None:
            scalar_vars = set()
        if dict_vars is None:
            dict_vars = set()

        self._s_vars = scalar_vars
        self._d_vars = dict_vars

        self._k_domain = key_domain
        self._v_domain = value_domain

        self._s_domain = scalar_domain
        self._scalar_state = scalar_domain(scalar_vars)         # require as input?

        arguments = {}
        for dv in dict_vars:
            typ = dv.typ
            if isinstance(typ, DictLyraType):  # should be true
                if typ not in arguments:
                    # if issubclass(key_domain, Store):   # not relational -> don't need scalar vars
                    #     key_vars = []
                    # else:
                    # key_vars = scalar_vars.copy()
                    # if issubclass(value_domain, Store):
                    #     value_vars = []
                    # else:
                    # value_vars = scalar_vars.copy()
                    k_var = VariableIdentifier(typ.key_type, k_name)
                    v_var = VariableIdentifier(typ.value_type, v_name)

                    arguments[typ] = {'key_domain': key_domain, 'value_domain': value_domain,
                                      'key_d_args': {'scalar_variables': scalar_vars,
                                                     'k_var': k_var},
                                      'value_d_args': {'scalar_variables': scalar_vars,
                                                       'v_var': v_var}}
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

        self._in_relations = InRelationState()

        self._loop_flag = False

    @property
    def scalar_state(self) -> Union[ScalarWrapper, State]:
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

    @property
    def in_relations(self) -> InRelationState:
        """Relational state storing relationships introduced by 'in'-conditions."""
        return self._in_relations

    @property
    def v_domain(self) -> Type[Union[ValueWrapper, State]]:
        """Domain for dictionary values"""
        return self._v_domain

    @property
    def k_domain(self) -> Type[Union[KeyWrapper, State]]:
        """Domain for dictionary keys"""
        return self._k_domain

    @property
    def s_k_conv(self):
        """Function to convert from scalar domain elements to key domain elements"""
        return self._s_k_conv

    @property
    def k_s_conv(self):
        """Function to convert from key domain elements to scalar domain elements"""
        return self._k_s_conv

    @property
    def s_v_conv(self):
        """Function to convert from scalar domain elements to value domain elements"""
        return self._s_v_conv

    @property
    def v_s_conv(self):
        """Function to convert from value domain elements to scalar domain elements"""
        return self._v_s_conv

    def __repr__(self):             # TODO: use join
        k_is_store = issubclass(self.k_domain, Store)
        v_is_store = issubclass(self.v_domain, Store)
        if k_is_store or v_is_store:
            # type does not matter, because eq is implemented in terms of name
            v_k = VariableIdentifier(LyraType(), k_name)
            v_v = VariableIdentifier(LyraType(), v_name)
            result = repr(self.scalar_state)
            for d, d_lattice in sorted(self.dict_store.store.items(), key=lambda t: t[0].name):
                result += f", {d} -> {{"
                first = True
                for (k, v) in d_lattice.sorted_segments():
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

            for d, i_lattice in sorted(self.init_store.store.items(), key=lambda t: t[0].name):
                result += f", {d} -> {{"
                first = True
                for (k, v) in i_lattice.sorted_segments():
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

            result += ", " + repr(self.in_relations)
            return result
        else:
            return f"{self.scalar_state}, {self.dict_store}, {self.init_store}"

    @copy_docstring(Lattice.bottom)
    def bottom(self) -> 'DictContentState':
        """The bottom lattice element is defined point-wise."""
        self.scalar_state.bottom()
        self.dict_store.bottom()
        self.init_store.bottom()
        self.in_relations.bottom()
        return self

    @copy_docstring(Lattice.top)
    def top(self) -> 'DictContentState':
        """The top lattice element is defined point-wise."""
        self.scalar_state.top()
        self.dict_store.top()
        self.init_store.top()
        self.in_relations.top()
        return self

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        """The current state is bottom if `all` of its four elements are bottom"""
        scalar_b = self.scalar_state.is_bottom()
        dict_b = self.dict_store.is_bottom()
        init_b = self.init_store.is_bottom()
        in_b = self.in_relations.is_bottom()
        return scalar_b and dict_b and init_b and in_b

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        """The current state is bottom if `all` of its four elements are top"""
        scalar_t = self.scalar_state.is_top()
        dict_t = self.dict_store.is_top()
        init_t = self.init_store.is_top()
        in_t = self.in_relations.is_top()
        return scalar_t and dict_t and init_t and in_t

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'DictContentState') -> bool:
        """Defined point-wise"""
        scalar_le = self.scalar_state.less_equal(other.scalar_state)
        dict_le = self.dict_store.less_equal(other.dict_store)
        init_le = self.init_store.less_equal(other.init_store)
        in_le = self.in_relations.less_equal(other.in_relations)
        return scalar_le and dict_le and init_le and in_le

    @copy_docstring(Lattice._join)
    def _join(self, other: 'DictContentState') -> 'DictContentState':
        """Defined point-wise"""
        self.scalar_state.join(other.scalar_state)
        self.dict_store.join(other.dict_store)
        self.init_store.join(other.init_store)
        self.in_relations.join(other.in_relations)
        return self

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'DictContentState'):
        """Defined point-wise"""
        self.scalar_state.meet(other.scalar_state)
        self.dict_store.meet(other.dict_store)
        self.init_store.meet(other.init_store)
        self.in_relations.meet(other.in_relations)
        return self

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'DictContentState'):
        """To avoid imprecise widening of DictSegmentLattice, first widens the scalar state"""
        old_scalar = deepcopy(self.scalar_state)
        self.scalar_state.widening(other.scalar_state)
        if old_scalar != self.scalar_state:
            self.dict_store.join(other.dict_store)
            self.init_store.join(other.init_store)
            self.in_relations.join(other.in_relations)
        else:
            self.dict_store.widening(other.dict_store)
            self.init_store.widening(other.init_store)
            self.in_relations.widening(other.in_relations)
        return self

    # helper
    def eval_key(self, key_expr: Expression) -> Union[KeyWrapper, State]:
        """evaluates key_expr in the scalar_state and assigns it to v_k in a key state"""
        scalar_copy = deepcopy(self.scalar_state)
        v_k = VariableIdentifier(key_expr.typ, k_name)       # TODO: type?
        scalar_copy.add_var(v_k)
        scalar_copy.assign({v_k}, {key_expr})

        return self._s_k_conv(scalar_copy)

    # helper
    def eval_value(self, value_expr: Expression) -> Union[ValueWrapper, State]:
        """evaluates value_expr in the scalar_state and assigns it to v_v in a value state"""
        scalar_copy = deepcopy(self.scalar_state)
        v_v = VariableIdentifier(value_expr.typ, v_name)  # TODO: type?
        scalar_copy.add_var(v_v)
        scalar_copy.assign({v_v}, {value_expr})

        return self._s_v_conv(scalar_copy)

    # helper
    def _temp_cleanup(self, evaluation: Dict[Subscription, VariableIdentifier]):
        """Deletes all temporary variables of evaluation
        and assigns them back to the dictionary subscription before that"""
        current_temps = set(evaluation.values())

        for expr, var in evaluation.items():
            # 'assign expr = var' to update relationships
            d = expr.target

            k_abs = self.eval_key(expr.key)
            v_abs = self.eval_value(var)

            # temporary variables not needed in dict abstractions
            for temp in current_temps:     # TODO: better way?
                k_abs.remove_var(temp)
                v_abs.remove_var(temp)

            d_lattice: 'DictSegmentLattice' = self.dict_store.store[d]

            if k_abs.is_singleton():
                # STRONG UPDATE
                d_lattice.partition_add(k_abs, v_abs)
                i_lattice: 'DictSegmentLattice' = self.init_store.store[d]
                i_lattice.partition_add(k_abs, BoolLattice(False))
            else:
                # WEAK UPDATE
                # -> meet
                assign_lattice = deepcopy(d_lattice)
                assign_lattice.normalized_add(k_abs, v_abs)
                d_lattice.meet(assign_lattice)

            # remove temporary var
            self.scalar_state.remove_var(var)
            current_temps.remove(var)

    def _update_dict_from_refined_scalar(self):
        """update scalar variables in dictionary stores to conform with a refined scalar state"""
        # TODO: too slow?
        d_store = self.dict_store.store
        d_lattice: DictSegmentLattice
        for d, d_lattice in d_store.items():
            v_k = VariableIdentifier(d.typ.key_type, k_name)
            v_v = VariableIdentifier(d.typ.value_type, v_name)
            new_segments = set()
            for (k, v) in d_lattice.segments:
                k_s_state = deepcopy(self.scalar_state)
                k_s_state.add_var(v_k)
                s_k_state = self.s_k_conv(k_s_state)
                new_k = deepcopy(k).meet(s_k_state)

                v_s_state = deepcopy(self.scalar_state)
                v_s_state.add_var(v_v)
                s_v_state = self.s_v_conv(v_s_state)
                new_v = deepcopy(v).meet(s_v_state)
                new_segments.add((new_k, new_v))
            d_store[d] = DictSegmentLattice(d_lattice.k_domain, d_lattice.v_domain,
                                            d_lattice.k_d_args, d_lattice.v_d_args, new_segments)

        i_store = self.init_store.store
        i_lattice: DictSegmentLattice
        for d, i_lattice in i_store.items():
            v_k = VariableIdentifier(d.typ.key_type, k_name)

            new_segments = set()
            for (k, b) in i_lattice.segments:
                k_s_state = deepcopy(self.scalar_state)
                k_s_state.add_var(v_k)
                s_k_state = self.s_k_conv(k_s_state)
                new_k = deepcopy(k).meet(s_k_state)
                new_segments.add((new_k, b))
            i_store[d] = DictSegmentLattice(i_lattice.k_domain, i_lattice.v_domain,
                                            i_lattice.k_d_args, i_lattice.v_d_args, new_segments)

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        all_ids = left.ids().union(right.ids())

        if all(type(id.typ) in scalar_types for id in all_ids):   # TODO: use not any?
            # completely SCALAR STMT
            # update scalar part
            self.scalar_state.assign({left}, {right})

            # update relations with scalar variables in dict stores
            for d_lattice in self.dict_store.store.values():
                for (k1, v) in d_lattice.segments:
                    k1.assign({left}, {right})
                    v.assign({left}, {right})
                d_lattice.d_norm_own()
            for i_lattice in self.init_store.store.values():
                for (k2, b) in i_lattice.segments:        # b must be True
                    k2.assign({left}, {right})
                i_lattice.d_norm_own()

        if isinstance(left, VariableIdentifier):
            if type(left.typ) in scalar_types:  # assignment to scalar variable
                evaluation = dict()
                scalar_right = self._read_eval.visit(right, self, evaluation)
                self.scalar_state.assign({left}, {scalar_right})

                self._temp_cleanup(evaluation)

                # invalidate old left in dict stores                      # IMPRECISION!!
                for d_lattice in self.dict_store.store.values():
                    d_lattice.invalidate_var(left)
                for i_lattice in self.init_store.store.values():
                    i_lattice.invalidate_var(left)

            elif isinstance(left.typ, DictLyraType):    # overwrite dictionary
                if isinstance(right, VariableIdentifier):
                    self.dict_store.store[left] = deepcopy(self.dict_store.store[right])        # TODO: alias -> don't copy?
                    self.init_store.store[left] = deepcopy(self.init_store.store[right])
                elif isinstance(right, DictDisplay):
                    # "NEW DICT"
                    left_lattice: DictSegmentLattice = self.dict_store.store[left]
                    left_i_lattice: DictSegmentLattice = self.init_store.store[left]
                    # erase all dict contents before:
                    left_lattice.bottom()
                    # everything uninitialized,
                    # but scalars should conform with scalar state -> copy from scalar state:
                    # TODO: use invalidate_var?
                    v_k = VariableIdentifier(left.typ.key_type, k_name)
                    s_state = deepcopy(self.scalar_state)
                    s_state.add_var(v_k)
                    top_state = self.s_k_conv(s_state)
                    top_segment = (top_state, BoolLattice(True))
                    left_i_lattice.segments.clear()
                    left_i_lattice.segments.add(top_segment)

                    for i in range(len(right.keys)):  # similar to write
                        k_abs = self.eval_key(right.keys[i])
                        v_abs = self.eval_value(right.values[i])

                        # k_abs must be a singleton -> 'strong update'
                        left_lattice.partition_add(k_abs, v_abs)
                        left_i_lattice.partition_add(k_abs, BoolLattice(False))
                else:
                    raise NotImplementedError(
                        f"Assignment '{left} = {right}' is not yet supported")
            else:
                raise NotImplementedError(
                    f"Assignment '{left} = {right}' is not yet supported")

        elif isinstance(left, Subscription) and isinstance(left.target.typ, DictLyraType):
            # DICT WRITE
            d = left.target

            k_abs = self.eval_key(left.key)

            evaluation = dict()
            scalar_right = self._read_eval.visit(right, self, evaluation)
            v_abs = self.eval_value(scalar_right)
            for temp in evaluation.values():
                v_abs.remove_var(temp)
            self._temp_cleanup(evaluation)      # TODO: no assign needed?

            d_lattice: 'DictSegmentLattice' = self.dict_store.store[d]

            if k_abs.is_singleton():
                # STRONG UPDATE
                d_lattice.partition_add(k_abs, v_abs)
                i_lattice: 'DictSegmentLattice' = self.init_store.store[d]
                i_lattice.partition_add(k_abs, BoolLattice(False))
            else:
                # WEAK UPDATE
                # add segment & normalize
                d_lattice.normalized_add(k_abs, v_abs)
        else:
            raise NotImplementedError(f"Assignment '{left} = {right}' is not yet supported")
        # TODO: other stmts

        # update relations
        self.in_relations.assign({left}, {right})

        return self

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'DictContentState':
        condition = NegationFreeNormalExpression().visit(condition)     # eliminate negations

        if isinstance(condition, BinaryComparisonOperation):
            if condition.operator == BinaryComparisonOperation.Operator.In:
                # refine variable:
                if isinstance(condition.right, Keys) \
                        and isinstance(condition.left, VariableIdentifier):
                    d = condition.right.target_dict
                    d_lattice: DictSegmentLattice = self.dict_store.store[d]
                    k_abs: Union[KeyWrapper, State] = d_lattice.get_keys_joined()
                    v_k = k_abs.k_var

                    if self._loop_flag:  # loop condition -> overwrite old value
                        self.scalar_state.add_var(v_k)
                        self.scalar_state.meet(self._k_s_conv(k_abs))
                        self.scalar_state.assign({condition.left}, {v_k})
                        self.scalar_state.remove_var(v_k)

                        # invalidate old left in dict stores                      # IMPRECISION!!
                        for d_lattice in self.dict_store.store.values():
                            d_lattice.invalidate_var(condition.left)
                        for i_lattice in self.init_store.store.values():
                            i_lattice.invalidate_var(condition.left)
                    else:   # meet after assignment -> only refine old value
                        assign_state = self._k_s_conv(k_abs)
                        assign_state.assign({condition.left}, {v_k})
                        assign_state.remove_var(v_k)
                        self.scalar_state.meet(assign_state)
                        if self.scalar_state.is_bottom():   # not reachable
                            return self.bottom()
                        self._update_dict_from_refined_scalar()

                    # refine in_relations
                    self.in_relations.assume({condition})
                    return self
                elif isinstance(condition.right, Values) \
                        and isinstance(condition.left, VariableIdentifier):
                    d = condition.right.target_dict
                    d_lattice: DictSegmentLattice = self.dict_store.store[d]
                    v_abs: Union[ValueWrapper, State] = d_lattice.get_values_joined()
                    v_v = v_abs.v_var

                    if self._loop_flag:  # loop condition -> overwrite old value
                        self.scalar_state.add_var(v_v)
                        self.scalar_state.meet(self._v_s_conv(v_abs))
                        self.scalar_state.assign({condition.left}, {v_v})
                        self.scalar_state.remove_var(v_v)

                        # invalidate old left in dict stores                      # IMPRECISION!!
                        for d_lattice in self.dict_store.store.values():
                            d_lattice.invalidate_var(condition.left)
                        for i_lattice in self.init_store.store.values():
                            i_lattice.invalidate_var(condition.left)
                    else:   # meet after assignment -> only refine old value
                        assign_state = self._v_s_conv(v_abs)
                        assign_state.assign({condition.left}, {v_v})
                        assign_state.remove_var(v_v)
                        self.scalar_state.meet(assign_state)
                        if self.scalar_state.is_bottom():   # not reachable
                            return self.bottom()
                        self._update_dict_from_refined_scalar()

                    # refine in_relations
                    self.in_relations.assume({condition})
                    return self
                elif isinstance(condition.right, Items) \
                        and isinstance(condition.left, TupleDisplay):
                    d = condition.right.target_dict
                    d_lattice: DictSegmentLattice = self.dict_store.store[d]

                    k_abs: Union[KeyWrapper, State] = d_lattice.get_keys_joined()
                    v_k = k_abs.k_var

                    v_abs = d_lattice.get_values_joined()
                    v_v = v_abs.v_var

                    if self._loop_flag:  # loop condition -> overwrite old value
                        self.scalar_state.add_var(v_k)
                        self.scalar_state.meet(self._k_s_conv(k_abs))
                        self.scalar_state.assign({condition.left.items[0]}, {v_k})
                        self.scalar_state.remove_var(v_k)

                        self.scalar_state.add_var(v_v)
                        self.scalar_state.meet(self._v_s_conv(v_abs))
                        self.scalar_state.assign({condition.left.items[1]}, {v_v})
                        self.scalar_state.remove_var(v_v)

                        # invalidate old left in dict stores                      # IMPRECISION!!
                        for d_lattice in self.dict_store.store.values():
                            d_lattice.invalidate_var(condition.left.items[0])
                            d_lattice.invalidate_var(condition.left.items[1])
                        for i_lattice in self.init_store.store.values():
                            i_lattice.invalidate_var(condition.left.items[0])
                            i_lattice.invalidate_var(condition.left.items[1])
                    else:
                        k_s_state = self.k_s_conv(k_abs)
                        k_s_state.assign({condition.left.items[0]}, {v_k})
                        k_s_state.remove_var(v_k)

                        v_s_state = self.v_s_conv(v_abs)
                        v_s_state.assign({condition.left.items[1]}, {v_v})
                        v_s_state.remove_var(v_v)

                        assign_state = k_s_state
                        assign_state.meet(v_s_state)
                        self.scalar_state.meet(assign_state)
                        if self.scalar_state.is_bottom():   # not reachable
                            return self.bottom()
                        self._update_dict_from_refined_scalar()

                    # refine in_relations
                    self.in_relations.assume({condition})
                    return self
                else:
                    # refine in_relations
                    self.in_relations.assume({condition})
            elif condition.operator == BinaryComparisonOperation.Operator.NotIn:
                if isinstance(condition.right, Keys):
                    d = condition.right.target_dict
                    d_lattice: DictSegmentLattice = self.dict_store.store[d]
                    k_abs: Union[KeyWrapper, State] = d_lattice.get_keys_joined()
                    v_k = k_abs.k_var

                    s_current = deepcopy(self.scalar_state)
                    s_current.add_var(v_k)
                    s_current.assign({v_k}, {condition.left})
                    k_current = self.s_k_conv(s_current)
                    key_complement = k_current.decomp(k_current, k_abs)
                    joined_complement = k_current.big_join(list(key_complement))

                    if self._loop_flag:  # loop condition -> overwrite old value
                        self.scalar_state.add_var(v_k)
                        self.scalar_state.meet(self._k_s_conv(joined_complement))
                        self.scalar_state.assign({condition.left}, {v_k})
                        self.scalar_state.remove_var(v_k)

                        # invalidate old left in dict stores                      # imprecision
                        for d_lattice in self.dict_store.store.values():
                            d_lattice.invalidate_var(condition.left)
                        for i_lattice in self.init_store.store.values():
                            i_lattice.invalidate_var(condition.left)
                    else:
                        assign_state = self._k_s_conv(joined_complement)
                        assign_state.assign({condition.left}, {v_k})
                        assign_state.remove_var(v_k)
                        self.scalar_state.meet(assign_state)
                        if self.scalar_state.is_bottom():   # not reachable
                            return self.bottom()
                        self._update_dict_from_refined_scalar()

                    # refine in_relations
                    self.in_relations.assume({condition})
                    return self
                elif isinstance(condition.right, Values):
                    # TODO
                    if self._loop_flag:
                        self.scalar_state.invalidate_var(condition.left)

                        # invalidate old left in dict stores                      # imprecision
                        for d_lattice in self.dict_store.store.values():
                            d_lattice.invalidate_var(condition.left)
                        for i_lattice in self.init_store.store.values():
                            i_lattice.invalidate_var(condition.left)

                    # refine in_relations
                    self.in_relations.assume({condition})
                    return self
                elif isinstance(condition.right, Items):
                    d = condition.right.target_dict
                    d_lattice: DictSegmentLattice = self.dict_store.store[d]
                    k_abs: Union[KeyWrapper, State] = d_lattice.get_keys_joined()
                    v_k = k_abs.k_var

                    s_current = deepcopy(self.scalar_state)
                    s_current.add_var(v_k)
                    s_current.assign({v_k}, {condition.left.items[0]})
                    k_current = self.s_k_conv(s_current)
                    key_complement = k_current.decomp(k_current, k_abs)
                    joined_complement = k_current.big_join(list(key_complement))

                    if self._loop_flag:  # loop condition -> overwrite old value
                        self.scalar_state.add_var(v_k)
                        self.scalar_state.meet(self._k_s_conv(joined_complement))
                        self.scalar_state.assign({condition.left.items[0]}, {v_k})
                        self.scalar_state.remove_var(v_k)

                        # invalidate old left in dict stores                      # imprecision
                        for d_lattice in self.dict_store.store.values():
                            d_lattice.invalidate_var(condition.left.items[0])
                            d_lattice.invalidate_var(condition.left.items[1])
                        for i_lattice in self.init_store.store.values():
                            i_lattice.invalidate_var(condition.left.items[0])
                            i_lattice.invalidate_var(condition.left.items[1])
                    else:
                        assign_state = self._k_s_conv(joined_complement)
                        assign_state.assign({condition.left.items[0]}, {v_k})
                        assign_state.remove_var(v_k)
                        self.scalar_state.meet(assign_state)
                        if self.scalar_state.is_bottom():   # not reachable
                            return self.bottom()
                        self._update_dict_from_refined_scalar()

                    # refine in_relations
                    self.in_relations.assume({condition})
                    return self
                else:
                    # refine in_relations
                    self.in_relations.assume({condition})

        # default: try in scalar domain
        evaluation = dict()
        scalar_condition = self._read_eval.visit(condition, self, evaluation)

        self.scalar_state.assume({scalar_condition})

        self._temp_cleanup(evaluation)

        # check, if coupled loop variables (from items-loops) get refined
        # -> refine their counterpart
        cond_vars = condition.ids()
        for (d_var, k_var, v_var) in self.in_relations.k_v_tuples():
            if k_var in cond_vars:
                if v_var in cond_vars:
                    raise NotImplementedError(
                        f"Conditions like {condition} containing both the key "
                        f"and value loop variable of a .items()-loop are not yet supported!")
                else:
                    # refine v_var according to refined k_var
                    # -> re-evaluate: v_var meet d_var[k_var]
                    d_lattice: DictSegmentLattice = self.dict_store.store[d_var]

                    k_abs = self.eval_key(k_var)

                    if not k_abs.is_top():          # TODO: check for less_equal old?
                        scalar_vars = self._s_vars.copy()
                        v_v = VariableIdentifier(d_var.typ.value_type, v_name)
                        v_abs = d_lattice.v_domain(scalar_vars, v_v).bottom()
                        for (k, v) in d_lattice.segments:
                            key_meet_k = deepcopy(k_abs).meet(k)
                            if not key_meet_k.is_bottom():  # key may be contained in this segment
                                v_abs.join(deepcopy(v))

                        scalar_copy = deepcopy(self.scalar_state)
                        scalar_copy.add_var(v_v)
                        scalar_copy.meet(self.v_s_conv(v_abs))
                        scalar_copy.assign({v_var}, {v_v})
                        scalar_copy.remove_var(v_v)

                        self.scalar_state.meet(scalar_copy)
            elif v_var in cond_vars:
                # refine k_var according to refined v_bar -> k_var, s.t. d_var[k_var] = v_var
                d_lattice: DictSegmentLattice = self.dict_store.store[d_var]

                v_abs = self.eval_key(v_var)

                if not v_abs.is_top():  # TODO: check for less_equal old?
                    scalar_vars = self._s_vars.copy()
                    v_k = VariableIdentifier(d_var.typ.key_type, k_name)
                    k_abs = d_lattice.k_domain(scalar_vars, v_k).bottom()
                    for (k, v) in d_lattice.segments:
                        value_meet_v = deepcopy(v_abs).meet(v)
                        if not value_meet_v.is_bottom():  # value may be contained in this segment
                            k_abs.join(deepcopy(k))

                    scalar_copy = deepcopy(self.scalar_state)
                    scalar_copy.add_var(v_k)
                    scalar_copy.meet(self.k_s_conv(k_abs))
                    scalar_copy.assign({k_var}, {v_k})
                    scalar_copy.remove_var(v_k)

                    self.scalar_state.meet(scalar_copy)

        self._update_dict_from_refined_scalar()

        # no 'in'-condition -> no need to update in_relations
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'DictContentState':
        self._loop_flag = False
        return self  # nothing else to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'DictContentState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'DictContentState':
        self._loop_flag = True
        return self  # nothing else to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'DictContentState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'DictContentState':
        return self  # nothing to be done

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'DictContentState':
        raise RuntimeError("Unexpected substitute in a forward analysis!")

        # expression evaluation

    class DictReadEvaluation:
        """Visitor that performs the evaluation of dictionary reads in the DictContentDomain
        lattice by replacing them with a temporary (scalar) variable holding
        the corresponding value in the scalar state.

        Adapted from `ExpressionVisitor`.
        """

        @copy_docstring(ExpressionVisitor.visit)
        def visit(self, expr, *args, **kwargs):
            """
            :param expr: current expression
            :param state: current DictContentState
            :param evaluation: dictionary mapping from dictionary read expressions,
                that already got evaluated to temporary variables (VariableIdentifier)
            :return expression with replaced dictionary reads
            """
            method = 'visit_' + expr.__class__.__name__
            if hasattr(self, method):
                return getattr(self, method)(expr, *args, **kwargs)

            else:
                return self.default_visit(expr, *args, **kwargs)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state: 'DictContentState' = None,
                               evaluation=None):
            if isinstance(expr.target.typ, DictLyraType):
                if expr in evaluation:  # already evaluated
                    return evaluation[expr]
                else:
                    d = expr.target
                    d_lattice: DictSegmentLattice = state.dict_store.store[d]

                    k_abs = state.eval_key(expr.key)

                    for old_temp in evaluation.values():    # remove already added temp vars
                        k_abs.remove_var(old_temp)

                    scalar_vars = state._s_vars.copy()
                    v_var = VariableIdentifier(d.typ.value_type, v_name)
                    v_abs = d_lattice.v_domain(scalar_vars, v_var).bottom()
                    for (k, v) in d_lattice.segments:
                        key_meet_k = deepcopy(k_abs).meet(k)
                        if not key_meet_k.is_bottom():  # key may be contained in this segment
                            v_abs.join(deepcopy(v))

                    for old_temp in evaluation.values():    # add already added temp vars
                        v_abs.add_var(old_temp)

                    state.scalar_state.add_var(v_var)
                    state.scalar_state.meet(state.v_s_conv(v_abs))

                    # use increasing numbers for temp_var names
                    temp_var = VariableIdentifier(d.typ.value_type, str(len(evaluation)) + "v")
                    state.scalar_state.add_var(temp_var)

                    state.scalar_state.assign({temp_var}, {v_var})
                    state.scalar_state.remove_var(v_var)

                    evaluation[expr] = temp_var
                    return temp_var
            else:
                return self.default_visit(expr, state, evaluation)

        def default_visit(self, expr: Expression, state: 'DictContentState' = None,
                          evaluation=None):
            # default: visit & replace children (adapted from expressions._iter_child_exprs)
            new_expr = copy(expr)
            for name, field in new_expr.__dict__.items():
                if isinstance(field, Expression):
                    new_expr.__dict__[name] = self.visit(field, state, evaluation)  # replace
                elif isinstance(field, list):
                    for idx, item in enumerate(field):
                        if isinstance(item, Expression):
                            field[idx] = self.visit(item, state, evaluation)
            return new_expr

    _read_eval = DictReadEvaluation()  # static class member shared between all instances
