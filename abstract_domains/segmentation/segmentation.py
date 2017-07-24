from copy import deepcopy
from typing import Type

from abstract_domains.lattice import Lattice

from abstract_domains.segmentation.bounds import SingleVarLinearFormWithOctagonalComparison as Form
from core.expressions import Literal, VariableIdentifier


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

    def __eq__(self, other):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1 == b2:
                    return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1 < b2:
                    return True
        return False

    def __le__(self, other):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1 <= b2:
                    return True
        return False

    def __gt__(self, other):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1 > b2:
                    return True
        return False

    def __ge__(self, other):
        for b1 in self.bounds:
            for b2 in other.bounds:
                if b1 >= b2:
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


class Segmentation:
    def __init__(self, len_var, predicate_lattice: Type[Lattice], octagon):
        self._octagon = octagon
        self._len_var = len_var
        self._predicate_lattice = predicate_lattice
        self._limits = [Limit({Form(Literal(int, '0'), self._octagon)}), Limit({Form(len_var, self._octagon)})]
        self._predicates = [self._predicate_lattice().top()]
        self._possibly_empty = [True]

    @property
    def limits(self):
        """All limits of this segmentation (in increasing order)."""
        return self._limits

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

        # also update octagon in all bounds!
        for b in self.all_bounds():
            b.octagon = value

    def __len__(self):
        return len(self.predicates)

    def __str__(self):
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
                assert self.limits[i] <= self.limits[
                    i + 1], f"Limits not ordered: {self.limits[i]} !<= {self.limits[i+1]}"
            else:
                assert self.limits[i] < self.limits[i + 1]

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

    def unify(self, other: 'Segmentation', neutral_predicate_generator):
        """Unifies this segmentation **and** the other segmentation to let them coincide.
        
        **NOTE**: This potentially also modifies the actual parameter ``other``.
        
        Requires compatible extremal limits, i.e. at least one common bound in the lower limits, one common bound in 
        the upper limits (of ``self`` and ``other``).
        """
        assert self.limits[0] == other.limits[0], "The lower limits should be equal for unification."

        self._unify(other, neutral_predicate_generator, 0, 0)

    def _unify(self, other: 'Segmentation', neutral_predicate_generator, self_index: int, other_index: int):
        # TODO check if this subset_case can be merged into incomparable_case
        def handle_subset_case(seg1, seg2, i, j):
            """Handle the case where ``b1 > b2``, i.e. bounds ``b2`` is a subset of bounds ``b1``.
            
            Where ``b1`` are bounds of ``seg1`` at current index of ``seg1`` and ``b2`` are bounds of ``seg2`` at 
            current index of ``seg2``. 
            
            This method recursively calls :meth:`unify`.
            
            :param i: index of the starting limit of first segmentation
            :param j: index of the starting limit of second segmentation
            :param b1: bounds of the starting limit of first segmentation
            :param b2: bounds of the starting limit of second segmentation
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
                seg1._unify(seg2, neutral_predicate_generator, i,
                            j)  # TODO ★ check if switch of receiver, other-argument is OK
            else:
                # add new segment to seg1 with neutral element
                seg1.add_limit(i, Limit(deepcopy(b1_exclusive)), predicate_before=neutral_predicate_generator(),
                               possibly_empty_before=True, possibly_empty_after=seg1.possibly_empty[i])

        def handle_incomparable_case(seg1, seg2, i, j):
            """Handle the case where neither ``b1 < b2`` nor ``b1 > b2``.

            Where ``b1`` are bounds of ``seg1`` at current index of ``seg1`` and ``b2`` are bounds of ``seg2`` at 
            current index of ``seg2``. 

            This method recursively calls :meth:`unify`.

            :param i: index of the starting limit of first segmentation
            :param j: index of the starting limit of second segmentation
            :param b1: bounds of the starting limit of first segmentation
            :param b2: bounds of the starting limit of second segmentation
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
                               predicate_before=neutral_predicate_generator(),
                               possibly_empty_before=True, possibly_empty_after=seg2.possibly_empty[j])
            if b1_appearing_later_in_seg2:
                seg1.add_limit(i, Limit(deepcopy(b1_appearing_later_in_seg2)),
                               predicate_before=neutral_predicate_generator(),
                               possibly_empty_before=True, possibly_empty_after=seg1.possibly_empty[i])
            seg1._unify(seg2, neutral_predicate_generator, i, j)

        self_bounds = self.limits[self_index].bounds
        other_bounds = other.limits[other_index].bounds

        # recursion ending criteria
        if self_index == len(self) and other_index == len(other):
            assert self.limits[self_index] == other.limits[other_index], "The upper limits should be equal for " \
                                                                         "unification. "
            return
        elif self_index == len(self) - 1 and other_index == len(other):
            assert self.limits[self_index] == other.limits[other_index] == self.limits[
                self_index + 1], "All three remaining limits should be equal for " \
                                 "unification. "
            upper_bounds = self.limits[self_index + 1].bounds | self.limits[self_index] | other.limits[other_index]
            self.remove_limit(self_index)
            self.limits[len(self)] = deepcopy(upper_bounds)
            other.limits[len(other)] = deepcopy(upper_bounds)

        if self_bounds == other_bounds:
            # same lower bounds -> keep both current lower segments as they are
            self._unify(other, neutral_predicate_generator, self_index + 1, other_index + 1)
        elif self_bounds & other_bounds:  # at least one bound in common
            if self_bounds > other_bounds:
                handle_subset_case(self, other, self_index, other_index)
            elif self_bounds < other_bounds:
                # this call switches the roles of self and other, potentially continues recursion with switched roles
                # TODO check if this is a problem (see other TODO ★)
                handle_subset_case(other, self, other_index, self_index)
            else:  # incomparable (remember that set inclusion is no total order!)
                handle_incomparable_case(self, other, self_index, other_index)
        else:  # no bound in common
            # we know that we are not at the lower limit of the segmentations (since this have a common bound always)
            # merge consecutive segments in both segmentations (removing both limits b1 and b2 with no bound in common)
            self.remove_limit(self_index + 1)
            other.remove_limit(other_index + 1)
