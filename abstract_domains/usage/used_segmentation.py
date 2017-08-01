from copy import deepcopy
from numbers import Number
from typing import Set, List, Sequence

from abstract_domains.numerical.interval_domain import IntervalLattice
from abstract_domains.segmentation.bounds import VarFormOct
from abstract_domains.segmentation.segmentation import SegmentedList
from abstract_domains.stack import ScopeDescendCombineMixin
from abstract_domains.state import State
from abstract_domains.store import Store
from abstract_domains.usage.used import U, S, O, UsedLattice, Used
from core.expressions import Literal, VariableIdentifier, Expression, Index, ListDisplay
from core.expressions_tools import walk
from core.statements import ProgramPoint
from engine.result import AnalysisResult


class UsedSegmentedList(SegmentedList):
    def __init__(self, variables: List[VariableIdentifier], len_var,
                 octagon_analysis_result: AnalysisResult):
        super().__init__(variables, len_var, lambda: UsedLattice().bottom(), octagon_analysis_result)

    # noinspection PyPep8Naming
    def change_S_to_U(self):
        """Change previously S-annotated (used in outer scope) to U-annotated (definitely used)"""
        for i, p in enumerate(self.predicates):
            if self.predicates[i] == S:
                self.predicates[i].used = U

    # noinspection PyPep8Naming
    def change_SU_to_O(self):
        """Change previously U/S-annotated to O-annotated"""
        for i, p in enumerate(self.predicates):
            if self.predicates[i].used in [S, U]:
                self.predicates[i].used = O


class UsedSegmentationMixStore(ScopeDescendCombineMixin, Store, State):
    def __init__(self, int_vars, list_vars, list_len_vars, list_to_len_var, octagon_analysis_result):
        self._list_vars = list_vars
        super().__init__(int_vars + list_vars + list_len_vars, {int: UsedLattice, list: lambda: None})
        for var in list_vars:
            self.store[var] = UsedSegmentedList(int_vars + list_len_vars, list_to_len_var[var],
                                                octagon_analysis_result)

    def descend(self) -> 'UsedSegmentationMixStore':
        for var in self.store.values():
            var.descend()
        return self

    def combine(self, other: 'UsedSegmentationMixStore') -> 'UsedSegmentationMixStore':
        for var, used in self.store.items():
            used.combine(other.store[var])
        return self

    def _use(self, left: VariableIdentifier, right: Expression):
        if issubclass(left.typ, Number):
            if self.store[left].used in [Used.U, Used.S]:
                for e in walk(right):
                    if isinstance(e, VariableIdentifier) and issubclass(e.typ, Number):
                        self.store[e].used = U
                    elif isinstance(e, Index):
                        if e.target.typ == list:
                            self.store[e.target].set_predicate(e.index, UsedLattice(U))
                        else:
                            raise NotImplementedError(
                                f"Indexed variable is not of any Sequence type, but {e.target.typ}!")

        elif issubclass(left.typ, Sequence):
            # list1 = ...
            segmentation = self.store[left]
            if isinstance(right, VariableIdentifier):
                # list1 = list2
                self.store[right].replace(deepcopy(segmentation))
                self.store[right].change_S_to_U()
            elif isinstance(right, ListDisplay):
                # list1 = [x, y, 5, x+y]
                list_display = right

                for index, e in enumerate(list_display.items):
                    if segmentation.get_predicate_at_form_index(VarFormOct(
                            interval=IntervalLattice.from_constant(index))).used in [Used.U, Used.S]:
                        for identifier in e.ids():
                            self.store[identifier].used = U
        else:
            raise NotImplementedError(f"Method _use not implemented for {self.store[left].typ}!")
        return self

    def _kill(self, left: VariableIdentifier, right: Expression):
        if issubclass(left.typ, Number):
            if self.store[left].used in [Used.U, Used.S]:
                if left in [v for v, u in self.store.items() if v in right.ids()]:
                    self.store[left].used = U  # x is still used since it is used in assigned expression
                else:
                    self.store[left].used = O  # x is overwritten
        elif issubclass(left.typ, Sequence):
            # TODO this whole if is no longer correct when lists of lists are allowed, e.g. l = [a,2,l]
            if isinstance(right, VariableIdentifier):
                if right != left:  # if no self-assignemnt
                    self.store[left].change_SU_to_O()
            elif isinstance(right, ListDisplay):
                self.store[left].change_SU_to_O()
            else:
                raise NotImplementedError(f"Method _kill not implemented for right side {right.typ}!")
        else:
            raise NotImplementedError(f"Method _kill not implemented for {self.store[left].typ}!")
        return self

    def _access_variable(self, variable: VariableIdentifier) -> Set[Expression]:
        return {variable}

    def _assign_variable(self, left: Expression, right: Expression) -> 'UsedSegmentationMixStore':
        raise NotImplementedError("Variable assignment is not supported!")

    def _assume(self, condition: Expression) -> 'UsedSegmentationMixStore':
        used_vars = len(
            set([lat.used for lat in self.store.values() if isinstance(lat, UsedLattice)]).intersection(
                [Used.U, Used.O])
        ) > 0
        used_lists = any(
            [lat.suo[Used.U] > 0 or lat.suo[Used.O] > 0 for lat in self.store.values() if
             isinstance(lat, UsedListStartLattice)]
        )
        store_has_effect = used_vars or used_lists

        for e in walk(condition):
            if isinstance(e, VariableIdentifier):
                # update to U if exists a variable y in state that is either U or O (note that S is not enough)
                # or is set intersection, if checks if resulting list is empty
                if store_has_effect:
                    self.store[e].used = Used.U
            elif isinstance(e, Index):
                if isinstance(e.index, Literal):
                    if store_has_effect:
                        self.store[e.target].set_used_at(e.index.val)
                else:
                    raise NotImplementedError()

        return self

    def _evaluate_literal(self, literal: Expression) -> Set[Expression]:
        return {literal}

    def enter_loop(self):
        raise NotImplementedError("UsedSegmentationMixStore does not support enter_loop")

    def exit_loop(self):
        raise NotImplementedError("UsedSegmentationMixStore does not support exit_loop")

    def enter_if(self):
        raise NotImplementedError("UsedSegmentationMixStore does not support enter_if")

    def exit_if(self):
        raise NotImplementedError("UsedSegmentationMixStore does not support exit_if")

    def _output(self, output: Expression) -> 'UsedSegmentationMixStore':
        for variable in output.ids():
            if issubclass(variable.typ, Number):
                self.store[variable].used = U
            elif issubclass(variable.typ, Sequence):
                segmented_list_state = self.store[variable]
                # remove all but extremal limits
                for i in range(1, len(segmented_list_state.limits) - 1):
                    segmented_list_state.remove_limit(1)
                # set single remaining segment as used
                segmented_list_state.predicates[0].used = U
            else:
                raise NotImplementedError(f"Type {variable.typ} not yet supported!")
        return self  # nothing to be done

    def _substitute_variable(self, left: Expression, right: Expression) -> 'UsedSegmentationMixStore':
        if isinstance(left, VariableIdentifier):
            self._use(left, right)._kill(left, right)
            for var in self._list_vars:
                self.store[var].substitute_variable(left, right)
        else:
            raise NotImplementedError("Variable substitution for {} is not implemented!".format(left))
        return self

    def next(self, pp: ProgramPoint):
        for var in self._list_vars:
            self.store[var].next(pp)
