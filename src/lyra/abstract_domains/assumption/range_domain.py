"""
Range Abstract Domain
=====================

Non-relational abstract domain to be used for **input data assumption analysis**.
The set of possible values of a program variable in a state is represented as a value range.

:Authors: Caterina Urban and Madelin Schumacher
"""
from lyra.abstract_domains.assumption.assumption_domain import InputMixin
from lyra.abstract_domains.numerical.interval_domain import IntervalState, \
    copy_docstring, Input


class RangeState(IntervalState, InputMixin):
    """Range assumption analysis state. An element of the range assumption abstract domain.

    Map from each program variable to the value range representing its value.
    The value of all program variables is represented by the unbounded range by default.

    When reading input data, the corresponding range assumptions
    are stored in the class member ``inputs``, which is a map
    from each program point to the list of range assumptions on the input data read at that point.

    .. document private methods
    .. automethod:: RangeState._assume
    .. automethod:: RangeState._substitute
    """

    class ArithmeticExpressionRefinement(IntervalState.ArithmeticExpressionRefinement):

        @copy_docstring(IntervalState.ArithmeticExpressionRefinement.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            state.record(value)
            return state    # nothing to be done

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between instances
