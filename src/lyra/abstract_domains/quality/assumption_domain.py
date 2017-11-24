"""
Assumption Domain
==================

:Author: Caterina Urban and Madelin Schumacher
"""
from typing import List

from copy import deepcopy

from lyra.abstract_domains.quality.assumption_lattice import TypeLattice
from lyra.abstract_domains.state import State
from lyra.abstract_domains.store import Store
from lyra.core.expressions import Expression, VariableIdentifier, Subscription, ExpressionVisitor, \
    Slicing
from lyra.core.types import ListLyraType, IntegerLyraType, BooleanLyraType, FloatLyraType, \
    StringLyraType
from lyra.core.utils import copy_docstring


class AssumptionState(Store, State):
    """Assumption analysis state. An element of the assumption abstract domain.

    Map from each program variable to the assumption tuple representing its current assumptions.

    .. document private methods
    .. automethod:: AssumptionState._assign
    .. automethod:: AssumptionState._assume
    .. automethod:: AssumptionState._output
    .. automethod:: AssumptionState._substitute

    """

    def __init__(self, variables: List[VariableIdentifier]):
        types = [BooleanLyraType, IntegerLyraType, FloatLyraType, StringLyraType, ListLyraType]
        lattices = {typ: TypeLattice for typ in types}
        super().__init__(variables, lattices)

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression):
        error = 'AssumptionState for forward assign statement analysis is not supported!'
        raise NotImplementedError(error)

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'AssumptionState':
        return self._refinement.visit(condition, TypeLattice(), self)

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'AssumptionState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'AssumptionState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'AssumptionState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'AssumptionState':
        return self  # nothing to be done

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'AssumptionState':
        return self._refinement.visit(output, TypeLattice(), self)

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'AssumptionState':
        if isinstance(left, VariableIdentifier):
            assumption = deepcopy(self.store[left])
            self.store[left].top()
            return self._refinement.visit(right, assumption, self)
        elif isinstance(left, Subscription) or isinstance(left, Slicing):
            assumption = deepcopy(self.store[left])
            self.store[left.target].top()
            return self._refinement.visit(right, assumption, self)
        error = f'Substitution for {left} not yet implemented!'
        raise NotImplementedError(error)

    class AssumptionRefinement(ExpressionVisitor):
        """TODO return NotImplementedError instead of state"""
        def visit_Subscription(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_Literal(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_Slicing(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_BinaryBooleanOperation(self, expr, assumption=None, state=None):
            left = self.visit(expr.left, TypeLattice(), state)
            right = self.visit(expr.right, TypeLattice(), left)
            return right

        def visit_UnaryArithmeticOperation(self, expr, assumption=None, state=None):
            refined = TypeLattice.from_lyra_type(expr.typ).meet(assumption)
            return self.visit(expr.expression, refined, state)

        def visit_BinaryArithmeticOperation(self, expr, assumption=None, state=None):
            refined = TypeLattice.from_lyra_type(expr.typ).meet(assumption)
            left = self.visit(expr.left, refined, state)
            right = self.visit(expr.right, refined, left)
            return right

        def visit_BinaryComparisonOperation(self, expr, assumption=None, state=None):
            left = self.visit(expr.left, TypeLattice(), state)
            right = self.visit(expr.right, TypeLattice(), left)
            return right

        def visit_AttributeReference(self, expr, assumption=None, state=None):
            error = f'Refinement for a {expr.__class__.__name__} is not supported!'
            raise NotImplementedError(error)

        def visit_Input(self, expr, assumption=None, state=None):
            return state  # TODO

        def visit_ListDisplay(self, expr, assumption=None, state=None):
            return state  # nothing to be done

        def visit_UnaryBooleanOperation(self, expr, assumption=None, state=None):
            return self.visit(expr.expression, TypeLattice(), state)

        def visit_VariableIdentifier(self, expr, assumption=None, state=None):
            state.store[expr] = TypeLattice.from_lyra_type(expr.typ).meet(assumption)
            return state

    _refinement = AssumptionRefinement()