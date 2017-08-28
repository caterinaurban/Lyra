from copy import deepcopy
from math import inf
from typing import Type, List, Union

from abstract_domains.lattice import Lattice
from abstract_domains.numerical.interval_domain import IntervalLattice
from abstract_domains.numerical.linear_forms import InvalidFormError
from abstract_domains.numerical.octagon_domain import OctagonDomain, OctagonLattice
from abstract_domains.segmentation.bounds import VarFormOct
from core.cfg import Edge
from core.expressions import Literal, VariableIdentifier, Expression
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
        # NOTE the sorted() to make output order of bounds deterministic
        return f"{{{','.join(sorted(map(lambda b: f'【{str(b)}】',self.bounds)))}}}"

    def forget(self, var: VariableIdentifier):
        forget_indices = []
        for i, b in enumerate(self.bounds):
            if b.var == var:
                # var appears in this bound -> mark for removal
                forget_indices.append(i)

        for i in reversed(forget_indices):
            del self._bounds[i]


class SegmentedListLattice(Lattice):
    def __init__(self, len_var, predicate_lattice: Type[Lattice], octagon: OctagonLattice):
        super().__init__()
        self._octagon = octagon
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
        for i in range(start_limit, len(self.limits)):
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
        limit_after = segment_index + 1

        self.limits.insert(limit_after, limit)
        limit_after += 1  # update index of limit after inserted limit

        self.predicates.insert(segment_index + 1, deepcopy(self.predicates[segment_index]))
        segment_index_before = segment_index
        segment_index_after = segment_index + 1
        del segment_index

        if predicate_before:
            self.predicates[segment_index_before] = deepcopy(predicate_before)
        if predicate_after:
            self.predicates[segment_index_after] = deepcopy(predicate_after)
        self.possibly_empty[segment_index_before] = possibly_empty_before
        self.possibly_empty.insert(segment_index_after, possibly_empty_after)

        # self.check_limits()

    def remove_limit(self, index):
        """Remove the limit at ``index`` and join the neighboring segments.
        
        **NOTE**: This modifies the underlying data structures. Ensure you handle possible index shifts.
        """
        assert 0 < index < len(self._limits) - 1, "Invalid index. Cannot remove lower or upper limit of segmentation!"

        p_left = deepcopy(self._predicates[index - 1])
        p_right = deepcopy(self._predicates[index])
        self._predicates[index - 1] = p_left.join(p_right)
        self._possibly_empty[index - 1] = self._possibly_empty[index - 1] and self._possibly_empty[index]
        del self._predicates[index]
        del self._limits[index]
        del self._possibly_empty[index]

        # self.check_limits()

    def remove_segment(self, index):
        """Remove the segment at ``index`` and join the neighboring limits.
        
        The predicate at the segment removed gets lost through this operation.

        **NOTE**: This modifies the underlying data structures. Ensure you handle possible index shifts.
        """

        self.limits[index].bounds |= self.limits[index + 1].bounds

        del self._predicates[index]
        del self._limits[index + 1]
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
        assert least_upper_limit >= 0, f"The target index {index_form} is smaller equals the lower limit!"
        return least_upper_limit

    def _set_predicate_at_form_index(self, form: VarFormOct, predicate):
        """Sets the segments *potentially* covered by index (specified in canonical form) to ``predicate``."""
        self._set_predicate_in_form_range(form, form, True, predicate)

    def _set_predicate_at_index(self, index: int, predicate):
        """Sets the segments *potentially* covered at ``index`` to ``predicate``."""
        form_index = VarFormOct(interval=IntervalLattice.from_constant(index))
        self._set_predicate_at_form_index(form_index, predicate)

    def _set_predicate_in_interval(self, interval, predicate):
        """Sets the segments *potentially* covered by ``interval`` (**both** bounds inclusive) to ``predicate``."""
        lower_index_form = VarFormOct(interval=IntervalLattice.from_constant(
            interval.lower))
        upper_index_form = VarFormOct(interval=IntervalLattice.from_constant(
            interval.upper))
        self._set_predicate_in_form_range(lower_index_form, upper_index_form, True, predicate)

    def _set_predicate_in_form_range(self, lower_index_form: VarFormOct,
                                     upper_index_form: VarFormOct, upper_inclusive, predicate):
        """Set a predicate within a range specified by bounds in canonical form.
        
        NOTE: This is the main helper method for ``set_predicate`` variants.
        
        :param lower_index_form: the range lower index in canonical form
        :param upper_index_form: the range upper index in canonical form (inclusive/exclusive can be specified)
        :param upper_inclusive: if the upper index should be included in the range where predicate is set
        :param predicate: the predicate to set in the range or None to set the element to the least upper bound of the predicate domain
        """
        if upper_inclusive:
            upper_index_form = deepcopy(upper_index_form)
            upper_index_form.interval.add(1)

        if lower_index_form.interval.lower == -inf:
            lower_index_form = VarFormOct(interval=IntervalLattice.from_constant(0))
        if upper_index_form.interval.upper == inf:
            upper_index_form = VarFormOct(var=self._len_var)

        gl, lu, lu_inclusive = self.get_gl_lu(lower_index_form, upper_index_form)

        # remove all limits between the least_upper_limit and greatest_lower_limit
        ##########################################################################
        for i in reversed(list(range(gl + 1, lu))):
            self.remove_limit(i)
            lu -= 1

        # add the target lower bound/limit
        if self.limits[gl].eq_octagonal(lower_index_form, self.octagon):
            # add target lower bound to existing limit
            self.limits[gl].bounds.add(lower_index_form)

            new_predicate_index = gl
        else:
            # add new limit for target lower bound, DO NOT set the new predicate here
            # (do this later when also existence of target upper bound is guaranteed)
            self.add_limit(gl, Limit({lower_index_form}),
                           possibly_empty_before=True, possibly_empty_after=False)
            lu += 1  # index correction since limit was added

            new_predicate_index = gl + 1

        # add the target upper bound/limit, setting predicate in (possibly newly inserted) segment
        if self.limits[lu].eq_octagonal(upper_index_form, self.octagon):
            # add target upper bound to existing limit
            self.limits[lu].bounds.add(upper_index_form)
        else:
            # add new limit for target lower bound, set the new predicate here, DO NOT set the new predicate here
            # (do this later in separate step)
            self.add_limit(lu - 1, Limit({upper_index_form}),
                           possibly_empty_before=False, possibly_empty_after=True)
            lu += 1  # index correction since limit was added

        # set the target predicate to segment that is now guaranteed to be properly bounded
        if predicate:
            self.predicates[new_predicate_index] = predicate
        else:
            pass  # the predicate of inserted segment is left to the join of smashed segments

    def set_predicate(self, index: Union[Expression, IntervalLattice, int], predicate):
        """Set a predicate at an index specifiable with various types.
        
        NOTE: this method forwards command to appropriate helper methods.
        
        :param index: the index where to set the predicate as integer value, interval or expression
        :param predicate: the predicate to set at the index/indices
        """
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
            assert 0 <= index < inf, "The index should not be smaller 0 nor infinity!"
            self._set_predicate_at_index(index, predicate)
        elif isinstance(index, IntervalLattice):
            self._set_predicate_in_interval(index, predicate)
        else:
            raise TypeError(f"Invalid argument type {type(index)} for 'expr'!")

    def get_gl_lu(self, lower_index_form: VarFormOct, upper_index_form: VarFormOct):
        gl = self.greatest_lower_limit(lower_index_form)
        lu = self.least_upper_limit(upper_index_form)
        lu_inclusive = not self.limits[lu].lt_octagonal(upper_index_form, self.octagon)
        if lu_inclusive:
            assert gl <= lu, "Implementation Error: inconsistent greatest_lower_limit, " \
                             "least_upper_limit indices!"
        else:
            assert gl < lu, "Implementation Error: inconsistent greatest_lower_limit, " \
                            "least_upper_limit indices!"
        return gl, lu, lu_inclusive

    def get_gl_lu_at_expr(self, index: Expression):
        try:
            form = VarFormOct.from_expression(index)
            lower_index_form = form
            upper_index_form = deepcopy(form)
        except InvalidFormError:
            # index is not in single variable linear form, use fallback: evaluate index
            interval = self.octagon.evaluate(index)
            lower_index_form = IntervalLattice.from_constant(interval.lower),
            upper_index_form = IntervalLattice.from_constant(interval.upper)
        return self.get_gl_lu(lower_index_form, upper_index_form)

    def get_predicate_in_form_range(self, lower_index_form: VarFormOct, upper_index_form: VarFormOct, upper_inclusive):
        if not upper_inclusive:
            upper_index_form = deepcopy(upper_index_form)
            upper_index_form.interval.sub(1)
        gl, lu, lu_inclusive = self.get_gl_lu(lower_index_form, upper_index_form)
        # check if we have to include the predicate at the least upper bound (lu)
        pred = self.predicates[gl:lu + 1 if lu_inclusive else lu]
        return self._predicate_lattice().bottom().big_join(pred)

    # TODO add type tolerant function like set_predicate
    def get_predicate_at_form_index(self, form: VarFormOct):
        lower_index_form = form

        return self.get_predicate_in_form_range(lower_index_form, lower_index_form, True)

    def merge_equal_limits(self):
        for i in reversed(range(0, len(self.limits) - 1)):
            if self.limits[i].eq_octagonal(self.limits[i + 1], self.octagon):
                self.remove_segment(i)

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

    def bottom(self):
        for p in self.predicates:
            p.bottom()
        return self

    def is_top(self) -> bool:
        return all([p.is_top() for p in self.predicates])

    def is_bottom(self) -> bool:
        return all([p.is_bottom() for p in self.predicates])

    def unify(self, other: 'SegmentedListLattice', left_neutral_predicate_generator,
              right_neutral_predicate_generator=None):
        """Unifies this segmentation **and** the other segmentation to let them coincide.
        
        **NOTE**: This potentially also modifies the actual parameter ``other``.
        
        Requires compatible extremal limits, i.e. at least one common bound in the lower limits, one common bound in 
        the upper limits (of ``self`` and ``other``).
        """
        assert self.limits[0].eq_octagonal(other.limits[0],
                                           self.octagon), "The lower limits should be equal for unification."
        assert self.limits[-1].eq_octagonal(other.limits[-1],
                                            self.octagon), "The upper limits should be equal for unification."

        if not right_neutral_predicate_generator:
            right_neutral_predicate_generator = left_neutral_predicate_generator

        # prepare the joined octagon used for unification
        # TODO this is ugly because the joined octagon was already calculated in octagon analysis
        # TODO (but is difficult to access from here)
        octagon = deepcopy(self.octagon).join(other.octagon)

        self._unify(other, left_neutral_predicate_generator, right_neutral_predicate_generator, 0, 0, octagon)

        # TODO check if really not needed (should not if unify does always merge equal limits on the fly
        # self.merge_equal_limits()
        # other.merge_equal_limits()

    def _unify(self, other: 'SegmentedListLattice', left_neutral_predicate_generator, right_neutral_predicate_generator,
               self_index: int, other_index: int, octagon: OctagonLattice):
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
                # TODO ★ check if switch of receiver, other-argument is OK
                seg1._unify(seg2, seg1_neutral_predicate_generator, seg2_neutral_predicate_generator, i, j, octagon)
            else:
                seg1.limits[i].bounds -= b1_exclusive
                # add new segment to seg1 with neutral element
                seg1.add_limit(i, Limit(deepcopy(b1_exclusive)), predicate_before=seg1_neutral_predicate_generator(),
                               possibly_empty_before=True, possibly_empty_after=seg1.possibly_empty[i])
                seg1._unify(seg2, seg1_neutral_predicate_generator, seg2_neutral_predicate_generator, i, j, octagon)

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
            seg1._unify(seg2, left_neutral_predicate_generator, right_neutral_predicate_generator, i, j, octagon)

        assert self_index <= len(self) and other_index <= len(other)

        # recursion ending criteria
        if self_index == len(self) and other_index == len(other):
            assert self.limits[self_index].eq_octagonal(other.limits[other_index],
                                                        octagon), "The upper limits should be equal for " \
                                                                  "unification. "
            # make syntactically equivalent too
            self.limits[self_index].bounds &= other.limits[other_index].bounds
            other.limits[other_index].bounds &= self.limits[self_index].bounds
            return
        elif self_index == len(self):
            # remove not visited limits from other
            for j in reversed(range(other_index, len(other))):
                other.remove_limit(j)
            # now other_index points to last limit of other
            assert other_index == len(other)
            # make syntactically equivalent too
            self.limits[self_index].bounds &= other.limits[other_index].bounds
            other.limits[other_index].bounds &= self.limits[self_index].bounds
            return
        elif other_index == len(other):
            # remove not visited limits from self
            for i in reversed(range(self_index, len(self))):
                self.remove_limit(i)
            # now self_index points to last limit of self
            assert self_index == len(self)
            # make syntactically equivalent too
            self.limits[self_index].bounds &= other.limits[other_index].bounds
            other.limits[other_index].bounds &= self.limits[self_index].bounds
            return

        self_limit = self.limits[self_index]
        other_limit = other.limits[other_index]
        self_bounds = self.limits[self_index].bounds
        other_bounds = other.limits[other_index].bounds

        # continue recursion
        if self_bounds == other_bounds:
            # same lower bounds -> keep both current lower segments as they are
            self._unify(other, left_neutral_predicate_generator, right_neutral_predicate_generator, self_index + 1,
                        other_index + 1, octagon)
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

            # check if b1 and b2 are orderable, either by octagonal comparision or syntactical check
            # NOTE: the syntactical check is necessary because octagon does NOT know that list__len >= every bound
            self_le = self_limit.le_octagonal(other_limit, octagon) or other_index == len(other)
            other_le = other_limit.le_octagonal(self_limit, octagon) or self_index == len(self)
            if self_le and other_le:
                # they are even equal -> merge to one limit
                self_limit.bounds |= deepcopy(other_limit.bounds)
                other_limit.bounds |= deepcopy(self_limit.bounds)
            elif self_le:
                other.add_limit(other_index - 1, deepcopy(self_limit),
                                possibly_empty_before=self.possibly_empty[self_index - 1],
                                possibly_empty_after=self.possibly_empty[self_index])
            elif other_le:
                self.add_limit(self_index - 1, deepcopy(other_limit),
                               possibly_empty_before=other.possibly_empty[other_index - 1],
                               possibly_empty_after=other.possibly_empty[other_index])
            else:
                # merge consecutive segments in both segmentations
                # (removing both limits b1 and b2 with no bound in common and not orderable)
                # TODO check if this if conditions are correct (are they missing in reference paper?)
                if self_index != len(self):
                    self.remove_limit(self_index)
                if other_index != len(other):
                    other.remove_limit(other_index)
                self_index -= 1
                other_index -= 1
            self._unify(other, left_neutral_predicate_generator,
                        right_neutral_predicate_generator, self_index, other_index, octagon)


class SegmentedList(SegmentedListLattice):
    def __init__(self, variables: List[VariableIdentifier], len_var, predicate_lattice: Type[Lattice],
                 octagon_analysis_result: AnalysisResult):
        super().__init__(len_var, predicate_lattice, octagon=OctagonDomain(variables).top())
        self._variables = variables
        self._octagon_analysis_result = octagon_analysis_result

    @property
    def variables(self):
        return self._variables

    @property
    def octagon_analysis_result(self):
        return self._octagon_analysis_result

    def substitute_variable(self, left: Expression, right: Expression) -> 'SegmentedList':
        if isinstance(left, VariableIdentifier):
            if left.typ == int:
                try:
                    form = VarFormOct.from_expression(right)
                    for bound in self.all_bounds():
                        bound.substitute_variable(left, form)
                    self.merge_equal_limits()
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
                                break  # break because bounds may have changed and all_bounds generator is disrupted
                        if not seen:
                            break
            else:
                # nothing to be done
                pass
        else:
            raise NotImplementedError()

        return self

    def next(self, pp: ProgramPoint, edge_kind: Edge.Kind = None):
        self.octagon = self.octagon_analysis_result.get_result_after(pp, edge_kind)
