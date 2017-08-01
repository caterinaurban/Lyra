from copy import deepcopy
from typing import Type, List, Union

from abstract_domains.lattice import Lattice, BottomMixin
from abstract_domains.numerical.interval_domain import IntervalLattice
from abstract_domains.numerical.linear_forms import InvalidFormError
from abstract_domains.numerical.octagon_domain import OctagonDomain, OctagonLattice
from abstract_domains.segmentation.bounds import VarFormOct
from abstract_domains.state import State
from core.expressions import Literal, VariableIdentifier, Expression
from core.expressions_tools import PLUS, MINUS
from core.statements import ProgramPoint
from engine.result import AnalysisResult


def _auto_convert_to_limit(func):
    def func_wrapper(self, other, *args, **kwargs):
        if not isinstance(other, Limit):
            other = Limit({other})

        return func(self, other, *args, **kwargs)

    return func_wrapper


class Limit:
    def __init__(self, bounds: set):
        self._bounds = bounds

    @property
    def bounds(self) -> set:
        return self._bounds

    @bounds.setter
    def bounds(self, value: set):
        self._bounds = value

    def __len__(self):
        return len(self.bounds)

    @_auto_convert_to_limit
    def eq_octagonal(self, other, octagon: OctagonLattice):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1.eq_octagonal(b2, octagon):
                    return True
        return False

    @_auto_convert_to_limit
    def ne_octagonal(self, other, octagon: OctagonLattice):
        return not self.eq_octagonal(other, octagon)

    @_auto_convert_to_limit
    def lt_octagonal(self, other, octagon: OctagonLattice):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1.lt_octagonal(b2, octagon):
                    return True
        return False

    @_auto_convert_to_limit
    def le_octagonal(self, other, octagon: OctagonLattice):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1.le_octagonal(b2, octagon):
                    return True
        return False

    @_auto_convert_to_limit
    def gt_octagonal(self, other, octagon: OctagonLattice):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1.gt_octagonal(b2, octagon):
                    return True
        return False

    @_auto_convert_to_limit
    def ge_octagonal(self, other, octagon: OctagonLattice):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1.ge_octagonal(b2, octagon):
                    return True
        return False

    def __str__(self):
        return f"{{{','.join(map(lambda b: f'【{str(b)}】',self.bounds))}}}"

    def forget(self, var: VariableIdentifier):
        forget_indices = []
        for i, b in enumerate(self.bounds):
            if b.var == var:
                # var appears in this bound -> mark for removal
                forget_indices.append(i)

        for i in reversed(forget_indices):
            del self._bounds[i]


class SegmentedListLattice(BottomMixin):
    def __init__(self, len_var, predicate_lattice: Type[Lattice], octagon: OctagonLattice):
        super().__init__()
        self._octagon = octagon  # TODO should we make copy? maybe yes since we add pseudo constraints var < len_var
        self._len_var = len_var
        self._predicate_lattice = predicate_lattice
        self._limits = [
            Limit({VarFormOct.from_expression(Literal(int, '0'))}),
            Limit({VarFormOct.from_expression(len_var)})]
        self._predicates = [self._predicate_lattice()]
        self._possibly_empty = [True]

    @property
    def limits(self):
        """All limits of this segmentation (in increasing order)."""
        return self._limits

    @property
    def lower_limit(self):
        return self.limits[0]

    @lower_limit.setter
    def lower_limit(self, value):
        self.limits[0] = value

    @property
    def upper_limit(self):
        return self.limits[len(self)]

    @upper_limit.setter
    def upper_limit(self, value):
        self.limits[len(self)] = value

    def all_bounds(self, start_limit=0):
        """Generate all bounds of all limits."""
        for i in range(start_limit, len(self._limits)):
            for b in self.limits[i].bounds:
                yield b

    @property
    def predicates(self):
        return self._predicates

    @property
    def possibly_empty(self):
        return self._possibly_empty

    @property
    def octagon(self):
        return self._octagon

    @octagon.setter
    def octagon(self, value):
        self._octagon = value

    def __len__(self):
        return len(self.predicates)

    def __repr__(self):
        s = ""
        for i in range(len(self)):
            s += str(self._limits[i])

            s_predicate = str(self.predicates[i])
            if self.possibly_empty[i]:
                s_predicate = f" {s_predicate} ?"
            else:
                s_predicate = f" {s_predicate} "
            s += s_predicate

        s += str(self._limits[-1])
        return f"[{s}]"

    def check_limits(self):
        for i in range(len(self)):
            if self.possibly_empty[i]:
                assert self.limits[i].le_octagonal(self.limits[
                                                       i + 1],
                                                   self.octagon), f"Limits not ordered: {self.limits[i]} !<= {self.limits[i+1]}"
            else:
                assert self.limits[i].lt_octagonal(self.limits[i + 1], self.octagon)

    def add_limit(self, segment_index, limit: Limit, predicate_before=None, predicate_after=None,
                  possibly_empty_before=True,
                  possibly_empty_after=True):
        """Add an additional limit at index, splitting the segment there."""
        limit_before = segment_index
        limit_after = segment_index + 1

        self.limits.insert(limit_after, limit)
        limit_after += 1  # update index of limit after inserted limit

        self.predicates.insert(segment_index + 1, self.predicates[segment_index])
        segment_index_before = segment_index
        segment_index_after = segment_index + 1
        del segment_index

        if predicate_before:
            self.predicates[segment_index_before] = predicate_before
        if predicate_after:
            self.predicates[segment_index_after] = predicate_after
        self.possibly_empty[segment_index_before] = possibly_empty_before
        self.possibly_empty.insert(segment_index_after, possibly_empty_after)

        # self.check_limits()

    def remove_limit(self, index):
        """Remove the limit at ``index`` and join the neighboring segments.
        
        **NOTE**: This modifies the underlying data structures. Ensure you handle possible index shifts.
        """
        assert 0 < index < len(self._limits) - 1, "Invalid index. Cannot remove lower or upper limit of segmentation!"

        p_left = self._predicates[index - 1]
        p_right = self._predicates[index]
        self._predicates[index - 1] = p_left.join(p_right)
        self._possibly_empty[index - 1] = self._possibly_empty[index - 1] and self._possibly_empty[index]
        del self._predicates[index]
        del self._limits[index]
        del self._possibly_empty[index]

        # self.check_limits()

    def forget(self, var: VariableIdentifier):
        remove_indices = []
        for i, l in enumerate(self._limits):
            l.forget(var)
            if len(l) == 0:  # empty limit -> mark for removal
                remove_indices.append(i)

        for i in reversed(remove_indices):
            self.remove_limit(i)

    def greatest_lower_limit(self, index_form):
        greatest_lower_limit = 0
        if index_form.interval.finite():
            while greatest_lower_limit < len(self) and self.limits[greatest_lower_limit + 1].le_octagonal(index_form,
                                                                                                          self.octagon):
                greatest_lower_limit += 1
        assert greatest_lower_limit < len(
            self), f"The target index {index_form} is greater than the length!"
        return greatest_lower_limit

    def least_upper_limit(self, index_form):
        """Finds least upper limit that is greater **or equals** to the index."""
        least_upper_limit = len(self)
        if index_form.interval.finite():
            while 0 < least_upper_limit and self.limits[least_upper_limit - 1].ge_octagonal(index_form, self.octagon):
                least_upper_limit -= 1
        assert least_upper_limit > 0, f"The target index {index_form} is smaller equals the lower limit!"
        return least_upper_limit

    def _set_predicate_at_form_index(self, form: VarFormOct, predicate):
        lower_index_form = form
        upper_index_form = deepcopy(form)
        upper_index_form.interval.add(1)

        self._set_predicate_in_form_range(lower_index_form, upper_index_form, predicate)

    def _set_predicate_at_index(self, index: int, predicate):
        form_index = VarFormOct(interval=IntervalLattice.from_constant(index))
        self._set_predicate_at_form_index(form_index, predicate)

    def _set_predicate_in_interval(self, interval, predicate):
        lower_form = VarFormOct(interval=IntervalLattice.from_constant(
            interval.lower))
        upper_form = VarFormOct(interval=IntervalLattice.from_constant(
            interval.upper))
        self._set_predicate_in_form_range(lower_form, upper_form, predicate)

    def _add_constraints_that_ensure_within_extremal_limits(self, form: VarFormOct):
        # since we presume out-of-bounds checks have been done before, we add octagonal constraints for:
        # -> index_forms are greater equals 0
        # -> index_forms are smaller than len_var
        # TODO or better add a synctatical 'rule' that knows that all variables are 0 <= var < n ?
        if form.var and form.var != self._len_var:
            self.octagon.set_lb(form.var, 0 - form.constant)
            self.octagon.set_octagonal_constraint(PLUS, form.var, MINUS, self._len_var, -1 - form.constant)

    def _set_predicate_in_form_range(self, lower_index_form: VarFormOct,
                                     upper_index_form: VarFormOct, predicate):
        """Main helper method. Set a predicate within a range given by bounds in linear form.
        
        :param predicate: the predicate to set in the range or None to set the element to the least upper bound of the predicate domain
        """
        # self._add_constraints_that_ensure_within_extremal_limits(lower_index_form)
        # self._add_constraints_that_ensure_within_extremal_limits(upper_index_form)

        greatest_lower_limit = self.greatest_lower_limit(lower_index_form)
        least_upper_limit = self.least_upper_limit(upper_index_form)

        assert greatest_lower_limit < least_upper_limit, "Implementation Error: inconsistent greatest_lower_limit, " \
                                                         "least_upper_limit indices!"

        # remove all limits between the least_upper_limit and greatest_lower_limit
        ##########################################################################
        for i in reversed(list(range(greatest_lower_limit + 1, least_upper_limit))):
            self.remove_limit(i)
            least_upper_limit -= 1

        # add the target lower bound/limit
        if self.limits[greatest_lower_limit].eq_octagonal(lower_index_form, self.octagon):
            # add target lower bound to existing limit
            self.limits[greatest_lower_limit].bounds.add(lower_index_form)

            new_predicate_index = greatest_lower_limit
        else:
            # add new limit for target lower bound, DO NOT set the new predicate here
            # (do this later when also existence of target upper bound is guaranteed)
            self.add_limit(greatest_lower_limit, Limit({lower_index_form}),
                           possibly_empty_before=True, possibly_empty_after=False)
            least_upper_limit += 1  # index correction since limit was added

            new_predicate_index = greatest_lower_limit + 1

        # add the target upper bound/limit, setting predicate in (possibly newly inserted) segment
        if self.limits[least_upper_limit].eq_octagonal(upper_index_form, self.octagon):
            # add target upper bound to existing limit
            self.limits[least_upper_limit].bounds.add(upper_index_form)
        else:
            # add new limit for target lower bound, set the new predicate here, DO NOT set the new predicate here
            # (do this later in separate step)
            self.add_limit(least_upper_limit - 1, Limit({upper_index_form}),
                           possibly_empty_before=False, possibly_empty_after=True)
            least_upper_limit += 1  # index correction since limit was added

        # set the target predicate to segment that is now guaranteed to be properly bounded
        if predicate:
            self.predicates[new_predicate_index] = predicate
        else:
            pass  # the predicate of inserted segment is left to the join of smashed segments

    def set_predicate(self, index: Union[Expression, IntervalLattice, int], predicate):
        # convert index to interval lattice
        if isinstance(index, Expression):
            # first try to represent the index as linear form
            try:
                form = VarFormOct.from_expression(index)
                self._set_predicate_at_form_index(form, predicate)
            except InvalidFormError:
                # Fallback: evaluate in octagon
                index_interval = self.octagon.evaluate(index)
                self._set_predicate_in_interval(index_interval, predicate)
        elif isinstance(index, int):
            self._set_predicate_at_index(index, predicate)
        elif isinstance(index, IntervalLattice):
            self._set_predicate_in_interval(index, predicate)
        else:
            raise TypeError(f"Invalid argument type {type(index)} for 'expr'!")

    # TODO add type tolerant function like set_predicate
    def get_predicate_at_form_index(self, form: VarFormOct):
        lower_index_form = form
        upper_index_form = deepcopy(form)
        upper_index_form.interval.add(1)

        gl = self.greatest_lower_limit(lower_index_form)
        lu = self.least_upper_limit(upper_index_form)
        return self._predicate_lattice().bottom().big_join(self.predicates[gl:lu])

    def _join(self, other: 'SegmentedListLattice') -> 'SegmentedListLattice':
        other_copy = deepcopy(other)
        self.unify(other_copy, lambda: self._predicate_lattice().bottom())
        for i in range(len(self)):
            self.predicates[i].join(other_copy.predicates[i])
            self.possibly_empty[i] = max(self.possibly_empty[i], other_copy.possibly_empty[i])
        return self

    def _less_equal(self, other: 'SegmentedListLattice') -> bool:
        other_copy = deepcopy(other)
        # different left/right neutral predicates!
        self.unify(other_copy, lambda: self._predicate_lattice().bottom(), lambda: self._predicate_lattice().top())
        return all(p1.less_equal(p2) for p1, p2 in zip(self.predicates, other_copy.predicates))

    def _widening(self, other: 'SegmentedListLattice'):
        other_copy = deepcopy(other)
        self.unify(other_copy, lambda: self._predicate_lattice().bottom())
        for p1, p2 in zip(self.predicates, other_copy.predicates):
            p1.widening(p2)
        return self

    def _meet(self, other: 'SegmentedListLattice'):
        other_copy = deepcopy(other)
        self.unify(other_copy, lambda: self._predicate_lattice().top())
        for i in range(len(self)):
            self.predicates[i].meet(other_copy.predicates[i])
            self.possibly_empty[i] = min(self.possibly_empty[i], other_copy.possibly_empty[i])
        return self

    def top(self):
        for p in self.predicates:
            p.top()
        return self

    def is_top(self) -> bool:
        return all([p.is_top() for p in self.predicates])

    def unify(self, other: 'SegmentedListLattice', left_neutral_predicate_generator,
              right_neutral_predicate_generator=None):
        """Unifies this segmentation **and** the other segmentation to let them coincide.
        
        **NOTE**: This potentially also modifies the actual parameter ``other``.
        
        Requires compatible extremal limits, i.e. at least one common bound in the lower limits, one common bound in 
        the upper limits (of ``self`` and ``other``).
        """
        assert self.limits[0].eq_octagonal(other.limits[0],
                                           self.octagon), "The lower limits should be equal for unification."

        if not right_neutral_predicate_generator:
            right_neutral_predicate_generator = left_neutral_predicate_generator

        self._unify(other, left_neutral_predicate_generator, right_neutral_predicate_generator, 0, 0)

    def _unify(self, other: 'SegmentedListLattice', left_neutral_predicate_generator, right_neutral_predicate_generator,
               self_index: int, other_index: int):
        # TODO check if this subset_case can be merged into incomparable_case
        def handle_subset_case(seg1, seg2, i, j, seg1_neutral_predicate_generator, seg2_neutral_predicate_generator):
            """Handle the case where ``b1 > b2``, i.e. bounds ``b2`` is a subset of bounds ``b1``.
            
            Where ``b1`` are bounds of ``seg1`` at current index of ``seg1`` and ``b2`` are bounds of ``seg2`` at 
            current index of ``seg2``. 
            
            This method recursively calls :meth:`unify`.
            
            :param seg1: segmentation 1
            :param seg2: segmentation 2
            :param i: index of the starting limit of first segmentation
            :param j: index of the starting limit of second segmentation
            :param seg1_neutral_predicate_generator: the neutral predicate generator for segmentation ``seg1``
            :param seg2_neutral_predicate_generator: the neutral predicate generator for segmentation ``seg2``
            """
            b1 = seg1.limits[self_index].bounds
            b2 = seg2.limits[other_index].bounds

            b1_exclusive = b1 - b2
            assert b1_exclusive, "Implementation error: There should be at least one bound exclusively in b1"
            assert not (b1_exclusive & b2), "Implementation error: b1_exclusive contains non-exclusive elements"

            # find bounds in b1_exclusive that do appear in any segmentation bounds from j+1 onwards
            b1_appearing_later_in_seg2 = b1_exclusive & set(seg2.all_bounds(j + 1))

            if not b1_appearing_later_in_seg2:  # if b1_exclusive bounds do not appear later in segmentation ``seg2``
                # just forget about b1_exclusive bounds
                seg1.limits[i].bounds -= b1_exclusive
                seg1._unify(seg2, seg1_neutral_predicate_generator, seg2_neutral_predicate_generator, i,
                            j)  # TODO ★ check if switch of receiver, other-argument is OK
            else:
                # add new segment to seg1 with neutral element
                seg1.add_limit(i, Limit(deepcopy(b1_exclusive)), predicate_before=seg1_neutral_predicate_generator(),
                               possibly_empty_before=True, possibly_empty_after=seg1.possibly_empty[i])

        def handle_incomparable_case(seg1, seg2, i, j):
            """Handle the case where neither ``b1 < b2`` nor ``b1 > b2``.

            Where ``b1`` are bounds of ``seg1`` at current index of ``seg1`` and ``b2`` are bounds of ``seg2`` at 
            current index of ``seg2``. 

            This method recursively calls :meth:`unify`.

            :param seg1: segmentation 1
            :param seg2: segmentation 2
            :param i: index of the starting limit of first segmentation
            :param j: index of the starting limit of second segmentation
            """
            b1 = seg1.limits[self_index].bounds
            b2 = seg2.limits[other_index].bounds

            b1_exclusive = b1 - b2
            b2_exclusive = b2 - b1
            assert b1_exclusive, "Implementation error: There should be at least one bound exclusively in b1"
            assert b2_exclusive, "Implementation error: There should be at least one bound exclusively in b2"
            assert not (b1_exclusive & b2), "Implementation error: b1_exclusive contains non-exclusive elements"
            assert not (b2_exclusive & b1), "Implementation error: b2_exclusive contains non-exclusive elements"

            # find bounds in b1_exclusive that do appear in any segmentation bounds from j+1 onwards
            b1_appearing_later_in_seg2 = b1_exclusive & set(seg2.all_bounds(j + 1))

            # find bounds in b2_exclusive that do appear in any segmentation bounds from i+1 onwards
            b2_appearing_later_in_seg1 = b2_exclusive & set(seg1.all_bounds(i + 1))

            # in all 4 cases we remove the respective exclusive bounds
            seg1.limits[i].bounds -= b1_exclusive
            seg2.limits[j].bounds -= b2_exclusive
            if b2_appearing_later_in_seg1:
                seg2.add_limit(j, Limit(deepcopy(b2_appearing_later_in_seg1)),
                               predicate_before=right_neutral_predicate_generator(),
                               possibly_empty_before=True, possibly_empty_after=seg2.possibly_empty[j])
            if b1_appearing_later_in_seg2:
                seg1.add_limit(i, Limit(deepcopy(b1_appearing_later_in_seg2)),
                               predicate_before=left_neutral_predicate_generator(),
                               possibly_empty_before=True, possibly_empty_after=seg1.possibly_empty[i])
            seg1._unify(seg2, left_neutral_predicate_generator, right_neutral_predicate_generator, i, j)

        self_bounds = self.limits[self_index].bounds
        other_bounds = other.limits[other_index].bounds

        # recursion ending criteria
        if self_index == len(self) and other_index == len(other):
            assert self.limits[self_index].eq_octagonal(other.limits[other_index],
                                                        self.octagon), "The upper limits should be equal for " \
                                                                       "unification. "
            return
        elif self_index == len(self) - 1 and other_index == len(other):
            assert self.limits[self_index].eq_octagonal(other.limits[other_index], self.octagon) and self.limits[
                self_index].eq_octagonal(self.limits[self_index + 1],
                                         self.octagon), "All three remaining limits should be equal for " \
                                                        "unification. "
            upper_bounds = self.limits[self_index + 1].bounds | self.limits[self_index].bounds | other.limits[
                other_index].bounds
            self.remove_limit(self_index)
            self.upper_limit = Limit(deepcopy(upper_bounds))
            other.lower_limit = Limit(deepcopy(upper_bounds))

        if self_bounds == other_bounds:
            # same lower bounds -> keep both current lower segments as they are
            self._unify(other, left_neutral_predicate_generator, right_neutral_predicate_generator, self_index + 1,
                        other_index + 1)
        elif self_bounds & other_bounds:  # at least one bound in common
            if self_bounds > other_bounds:
                handle_subset_case(self, other, self_index, other_index, left_neutral_predicate_generator,
                                   right_neutral_predicate_generator)
            elif self_bounds < other_bounds:
                # this call switches the roles of self and other, potentially continues recursion with switched roles
                # TODO check if this is a problem (see other TODO ★)
                handle_subset_case(other, self, other_index, self_index, right_neutral_predicate_generator,
                                   left_neutral_predicate_generator)
            else:  # incomparable (remember that set inclusion is no total order!)
                handle_incomparable_case(self, other, self_index, other_index)
        else:  # no bound in common
            # we know that we are not at the lower limit of the segmentations (since this have a common bound always)
            # merge consecutive segments in both segmentations (removing both limits b1 and b2 with no bound in common)
            self.remove_limit(self_index + 1)
            other.remove_limit(other_index + 1)


class SegmentedList(SegmentedListLattice):
    def __init__(self, variables: List[VariableIdentifier], len_var, predicate_lattice: Type[Lattice],
                 octagon_analysis_result: AnalysisResult):
        super().__init__(len_var, predicate_lattice, octagon=OctagonDomain(variables).top())
        self._variables = variables
        self._octagon_analysis_result = octagon_analysis_result
        self._next_pp = None

    @property
    def variables(self):
        return self._variables

    @property
    def octagon_analysis_result(self):
        return self._octagon_analysis_result

    @property
    def next_pp(self):
        return self._next_pp

    @next_pp.setter
    def next_pp(self, value):
        self._next_pp = value

    def substitute_variable(self, left: Expression, right: Expression) -> 'State':
        if isinstance(left, VariableIdentifier):
            if left.typ == int:
                try:
                    form = VarFormOct.from_expression(right)
                    for bound in self.all_bounds():
                        bound.substitute_variable(left, form)
                        # TODO check if limit order is preserved or cleanup necessary
                except InvalidFormError:
                    # right is not in single variable linear form, use fallback: evaluate right side of
                    # assignment in current octagon (transformed to interval) and use upper/lower of resulting
                    # interval to update segmentation
                    interval = self.octagon.evaluate(right)

                    while True:
                        seen = False
                        for b in self.all_bounds():
                            if b.var and b.var == left:  # substitution necessary
                                seen = True
                                self.set_predicate(interval + b.interval, self._predicate_lattice().top())
                        if not seen:
                            break
            else:
                # nothing to be done
                pass
        else:
            raise NotImplementedError()

        return self

    def next(self, pp: ProgramPoint):
        self.next_pp = pp
        self.octagon = self.octagon_analysis_result.get_result_after(self.next_pp)
