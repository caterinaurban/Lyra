from copy import deepcopy
from numbers import Number
from typing import Set, List, Sequence

from abstract_domains.numerical.interval_domain import IntervalLattice
from abstract_domains.numerical.linear_forms import InvalidFormError
from abstract_domains.segmentation.bounds import VarFormOct
from abstract_domains.segmentation.segmentation import SegmentedList
from abstract_domains.stack import ScopeDescendCombineMixin
from abstract_domains.state import State
from abstract_domains.store import Store
from abstract_domains.usage.used import U, S, O, UsedLattice, Used
from core.cfg import Edge
from core.expressions import VariableIdentifier, Expression, Index, ListDisplay
from core.expressions_tools import walk
from core.statements import ProgramPoint
from engine.result import AnalysisResult


class UsedSegmentedList(ScopeDescendCombineMixin, SegmentedList):
    def __init__(self, variables: List[VariableIdentifier], len_var,
                 octagon_analysis_result: AnalysisResult):
        super().__init__(variables, len_var, lambda: UsedLattice().bottom(), octagon_analysis_result)

    def descend(self) -> 'UsedSegmentedList':
        for i in range(len(self.predicates)):
            self.predicates[i].used = UsedLattice.DESCEND[self.predicates[i].used]
        return self

    def combine(self, other: 'UsedSegmentedList') -> 'UsedSegmentedList':
        self.unify(other, lambda: self._predicate_lattice().bottom())
        for i in range(len(self.predicates)):
            self.predicates[i].used = UsedLattice.COMBINE[(self.predicates[i].used, other.predicates[i].used)]
        return self

    # noinspection PyPep8Naming
    def change_S_to_U(self, predicate_indices=None):
        """Change previously S-annotated (used in outer scope) to U-annotated (definitely used).
         
        :param predicate_indices: limit the change to this indices
        """
        for i in predicate_indices if predicate_indices is not None else range(len(self.predicates)):
            if self.predicates[i].used == S:
                self.predicates[i].used = U

    # noinspection PyPep8Naming
    def change_SU_to_O(self, predicate_indices=None):
        """Change previously U/S-annotated to O-annotated.
        
        :param predicate_indices: limit the change to this indices
        """
        for i in predicate_indices if predicate_indices is not None else range(len(self.predicates)):
            if self.predicates[i].used in [S, U]:
                self.predicates[i].used = O


class UsedSegmentationStore(ScopeDescendCombineMixin, Store, State):
    def __init__(self, int_vars, list_vars, list_len_vars, list_to_len_var, octagon_analysis_result):
        self._list_vars = list_vars
        lattices = {int: lambda _: UsedLattice(),
                    list: lambda var: UsedSegmentedList(int_vars + list_len_vars, list_to_len_var[var],
                                                        octagon_analysis_result)}
        super().__init__(int_vars + list_vars + list_len_vars, lattices)

    def is_bottom(self) -> bool:
        """Test whether the used segmentation store is bottom, i.e. if *all* values in the store are bottom.

        **NOTE**: this is deviating definition of bottom from a usual mathematical store
        (where one value equals bottom is sufficient to let store be bottom)

        :return: whether the used segmentation store is bottom
        """
        return all(element.is_bottom() for element in self.store.values())

    def descend(self) -> 'UsedSegmentationStore':
        for lat in self.store.values():
            lat.descend()
        return self

    def combine(self, other: 'UsedSegmentationStore') -> 'UsedSegmentationStore':
        for var, lat in self.store.items():
            lat.combine(other.store[var])
        return self

    def _set_expr_used(self, expr: Expression):
        for e in walk(expr):
            if isinstance(e, VariableIdentifier) and issubclass(e.typ, Number):
                self.store[e].used = U
            elif isinstance(e, Index):
                if e.target.typ == list:
                    self.store[e.target].set_predicate(e.index, UsedLattice(U))
                else:
                    raise NotImplementedError(
                        f"Indexed variable is not of any Sequence type, but {e.target.typ}!")

    def _use(self, left: Expression, right: Expression):
        if isinstance(left, VariableIdentifier):
            if issubclass(left.typ, Number):
                if self.store[left].used in [Used.U, Used.S]:
                    self._set_expr_used(right)
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
                raise NotImplementedError(f"Method _use not implemented for left side variable of type {left.typ}!")
        elif isinstance(left, Index):
            segmentation = self.store[left.target]
            try:
                form = VarFormOct.from_expression(left.index)
                if segmentation.get_predicate_at_form_index(form).used in [Used.U, Used.S]:
                    self._set_expr_used(right)
            except InvalidFormError:
                # index is not in single variable linear form, use fallback: evaluate index
                interval = segmentation.octagon.evaluate(left.index)
                if segmentation.get_predicate_in_form_range(
                        VarFormOct(interval=IntervalLattice.from_constant(interval.lower)),
                        VarFormOct(interval=IntervalLattice.from_constant(interval.upper)), True).used in [Used.U,
                                                                                                           Used.S]:
                    self._set_expr_used(right)
        else:
            raise NotImplementedError(f"Method _use not implemented for left side type {type(left)}!")
        return self

    def _kill(self, left: VariableIdentifier, right: Expression):
        if isinstance(left, VariableIdentifier):
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
                    raise NotImplementedError(f"Method _kill not implemented for right side of type {right.typ}!")
            else:
                raise NotImplementedError(f"Method _kill not implemented for left side of type {self.store[left].typ}!")
        elif isinstance(left, Index):
            segmentation = self.store[left.target]
            # we have to 'kill' (change S,U to O) all indices where we are sure that this indices do not appear in right
            # find all indices that appear in right
            pred_indices_used_right = set()
            for e in walk(right):
                if isinstance(e, Index):
                    if e.target.typ == list:
                        if e.target == left.target:
                            gl, lu, lu_inclusive = segmentation.get_gl_lu_at_expr(e.index)
                            pred_indices_used_right |= set(range(gl, lu + 1 if lu_inclusive else lu))
                    else:
                        raise NotImplementedError(
                            f"Indexed variable is not of any Sequence type, but {e.target.typ}!")

            # find possible indices updates in the list on the left
            gl, lu, lu_inclusive = segmentation.get_gl_lu_at_expr(left.index)
            pred_indices_written_left = set(range(gl, min(len(segmentation), lu + 1 if lu_inclusive else lu)))
            pred_indices_overwritten = pred_indices_written_left - pred_indices_used_right
            segmentation.change_SU_to_O(pred_indices_overwritten)
        else:
            raise NotImplementedError(f"Method _kill not implemented for left side type {type(left)}!")
        return self

    def _access_variable(self, variable: VariableIdentifier) -> Set[Expression]:
        return {variable}

    def _assign_variable(self, left: Expression, right: Expression) -> 'UsedSegmentationStore':
        raise NotImplementedError("Variable assignment is not supported!")

    def _assume(self, condition: Expression) -> 'UsedSegmentationStore':
        used_vars = any([lat.used in [Used.U, Used.O] for lat in self.store.values() if isinstance(lat, UsedLattice)])
        used_lists = any([len(set(lat.predicates).intersection([Used.U, Used.O])) for lat in self.store.values() if
                          isinstance(lat, UsedSegmentedList)])
        store_has_effect = used_vars or used_lists

        for e in walk(condition):
            if isinstance(e, VariableIdentifier):
                # update to U if exists a variable y in state that is either U or O (note that S is not enough)
                # or is set intersection, if checks if resulting list is empty
                if store_has_effect:
                    self.store[e].used = Used.U
            elif isinstance(e, Index):
                self.store[e.target].set_predicate(e.index, UsedLattice(Used.U))
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

    def _output(self, output: Expression) -> 'UsedSegmentationStore':
        self._set_expr_used(output)
        return self

    def _substitute_variable(self, left: Expression, right: Expression,
                             only_substitute=False) -> 'UsedSegmentationStore':
        if isinstance(left, VariableIdentifier):
            if not only_substitute:
                self._use(left, right)._kill(left, right)
            for var in self._list_vars:
                self.store[var].substitute_variable(left, right)
        elif isinstance(left, Index):
            if not only_substitute:
                self._use(left, right)._kill(left, right)
        else:
            raise NotImplementedError("Variable substitution for {} is not implemented!".format(left))
        return self

    def next(self, pp: ProgramPoint, edge_kind: Edge.Kind = None):
        for var in self._list_vars:
            self.store[var].next(pp, edge_kind)
