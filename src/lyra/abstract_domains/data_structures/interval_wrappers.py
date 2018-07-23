from copy import deepcopy
from typing import Set

from lyra.abstract_domains.data_structures.key_wrapper import KeyWrapper
from lyra.abstract_domains.data_structures.scalar_wrapper import ScalarWrapper
from lyra.abstract_domains.data_structures.value_wrapper import ValueWrapper
from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.numerical.interval_domain import IntervalState, IntervalLattice
from lyra.core.expressions import VariableIdentifier
from lyra.core.utils import copy_docstring


class IntervalSWrapper(ScalarWrapper, IntervalState):
    """Wrapper around IntervalState for scalar domain of DictContentState"""

    def __init__(self, scalar_variables: Set[VariableIdentifier]):
        super().__init__(scalar_variables)

    @copy_docstring(ScalarWrapper.add_var)
    def add_var(self, var: VariableIdentifier):
        if var not in self.store.keys():
            self.variables.add(var)
            self.store[var] = IntervalLattice()     # top
        else:
            raise ValueError(f"Variable can not be added to a store if it is already present")

    @copy_docstring(ScalarWrapper.remove_var)
    def remove_var(self, var: VariableIdentifier):
        if var in self.store.keys():
            self.variables.remove(var)
            del self.store[var]
        else:
            raise ValueError(f"Variable can only be removed from a store if it is already present")

    @copy_docstring(ScalarWrapper.invalidate_var)
    def invalidate_var(self, var: VariableIdentifier):
        self.store[var].top()

    # def eval_value_at(self, dict: VariableIdentifier, k_interval: IntervalLattice) \
    #         -> 'IntervalLattice':
    #     # returns the join of all value abstraction of segments of dictionary dict,
    #     #  whose key overlaps with k_interval
    #     k_var = VariableIdentifier(dict.typ.value_type, dict_content_domain.k_name)
    #
    #     scalar_state = deepcopy(self)     # TODO: other args
    #     scalar_state.add_var(k_var)
    #     scalar_state.store[k_var] = k_interval
    #     k_state = self._dict_state.s_k_conv(scalar_state)
    #
    #     v_result = None  # bottom
    #     for (k, v) in self._dict_state.dict_store.store[dict].segments:
    #         key_meet_k = deepcopy(k_state).meet(k)
    #         if not key_meet_k.is_bottom():  # overlap/key may be contained in this segment
    #             if v_result is None:
    #                 v_result = v
    #             else:
    #                 v_result.join(v)
    #
    #     if v_result is not None:
    #         scalar_state = self._dict_state.v_s_conv(v_result)
    #         v_var = VariableIdentifier(dict.typ.value_type, dict_content_domain.v_name)
    #         return scalar_state.store[v_var]
    #     else:
    #         return IntervalLattice().bottom()

    # @copy_docstring(ScalarWrapper.dict_assume)
    # def dict_assume(self, condition: Expression, dict_state: DictContentState) -> 'IntervalSWrapper':
    #     self._dict_state = dict_state
    #     return self._assume(condition)
    #
    # def dict_assign(self, left: Expression, right: Expression, dict_state: DictContentState) -> 'IntervalSWrapper':
    #     self._dict_state = dict_state
    #     return self.assign({left}, {right})
    #
    # class ExtendedExprEvaluation(IntervalState.ExpressionEvaluation):
    #     # override
    #     @copy_docstring(ExpressionVisitor.visit_Subscription)
    #     def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
    #         if expr in evaluation:  # already evaluated
    #             return evaluation    # nothing to be done
    #         if isinstance(expr.target, VariableIdentifier) and isinstance(expr.target.typ, DictLyraType):
    #             # evaluate dictionary read
    #             evaluation = self.visit(expr.key, state, evaluation)
    #             k_interval = evaluation[expr.key]
    #             #k_abs = state._dict_state.eval_key(expr.key)
    #             #v_abs =
    #             res = state.eval_value_at(expr.target, k_interval)
    #             #v_var = VariableIdentifier(expr.target.typ.value_type, state._dict_state.v_name)
    #             evaluation[expr] = res#[v_var]
    #             return evaluation
    #
    #         evaluation[expr] = IntervalLattice()  # top -> be imprecise
    #         return evaluation
    #
    # _evaluation = ExtendedExprEvaluation()        # static class member shared between all instances

    # class ExtendedArithmeticExpressionRefinement(IntervalState.ArithmeticExpressionRefinement):
    #     # override
    #     @copy_docstring(ExpressionVisitor.visit_Subscription)
    #     def visit_Subscription(self, expr: Subscription, evaluation=None, value=None, state=None):
    #         if isinstance(expr.target, VariableIdentifier) and isinstance(expr.target.typ,
    #                                                                       DictLyraType):
    #             res_interval = evaluation[expr].meet(value)
    #             s_state = deepcopy(state)
    #             s_state.store
    #             state._dict_state.dict_store.store[expr.target] =
    #         return state
    #
    # _refinement = ExtendedArithmeticExpressionRefinement()


class IntervalKWrapper(KeyWrapper, IntervalSWrapper):
    """Wrapper around IntervalState for key domain of DictContentState"""

    def __init__(self, scalar_variables: Set[VariableIdentifier], k_var: VariableIdentifier):
        super().__init__(scalar_variables, k_var)

    @copy_docstring(KeyWrapper.decomp)
    def decomp(self, state: 'IntervalKWrapper', exclude: 'IntervalKWrapper') -> Set['IntervalKWrapper']:
        left = deepcopy(state)  # left & right non-exclude
        right = deepcopy(state)

        k_state = state.store[state.k_var]
        k_exclude = exclude.store[state.k_var]
        if k_state.is_bottom():
            left.store[state.k_var].bottom()
            right.store[state.k_var].bottom()
        elif k_exclude.is_bottom():
            left.store[state.k_var] = IntervalLattice(k_state.lower, k_state.upper)
            right.store[state.k_var].bottom()
        elif k_exclude.is_top():  # exclude everything
            left.store[state.k_var].bottom()
            right.store[state.k_var].bottom()
        else:
            left.store[state.k_var] = IntervalLattice(k_state.lower,
                                              k_exclude.lower - 1)  # bottom if empty
            right.store[state.k_var] = IntervalLattice(k_exclude.upper + 1,
                                               k_state.upper)  # bottom if empty

        return {left, right}

    @copy_docstring(KeyWrapper.is_singleton)
    def is_singleton(self) -> bool:
        key_interval = self.store[self.k_var]
        return (not key_interval.is_bottom()) and (key_interval.lower == key_interval.upper)

    def __eq__(self, other: 'Lattice'):
        return isinstance(other, self.__class__) and repr(self) == repr(other)

    def __ne__(self, other: 'Lattice'):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))

    @copy_docstring(KeyWrapper.__lt__)
    def __lt__(self, other):
        if isinstance(other, IntervalKWrapper):
            s_upper = self.store[self.k_var].upper
            o_lower = other.store[other.k_var].lower
            if s_upper < o_lower:       # other boundaries should conform with interval property by def
                return True
            else:
                return False
        return NotImplemented

    # @copy_docstring(KeyWrapper.__gt__)
    # def __gt__(self, other):
    #     if isinstance(other, IntervalKWrapper):
    #         s_upper = self.store[self.k_var].upper
    #         o_lower = other.store[other.k_var].lower
    #         if s_upper > o_lower:       # other boundaries should conform with interval property by def
    #             return True
    #         else:
    #             return False
    #     return NotImplemented

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self):
        return self.store[self.k_var].is_bottom()


class IntervalVWrapper(ValueWrapper, IntervalSWrapper):
    """Wrapper around IntervalState for value domain of DictContentState"""

    def __init__(self, scalar_variables: Set[VariableIdentifier], v_var: VariableIdentifier):
        super().__init__(scalar_variables, v_var)

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self):
        return self.store[self.v_var].is_bottom()       # TODO: in Superclass? (at least comment)

    def __eq__(self, other: 'Lattice'):
        return isinstance(other, self.__class__) and repr(self) == repr(other)

    def __ne__(self, other: 'Lattice'):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))