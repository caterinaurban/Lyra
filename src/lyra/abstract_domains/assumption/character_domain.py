import string
from collections import defaultdict
from typing import Set

from lyra.abstract_domains.assumption.assumption_domain import InputMixin
from lyra.abstract_domains.lattice import Lattice, BottomMixin
from lyra.abstract_domains.store import Store
from lyra.core.expressions import Expression, VariableIdentifier, ExpressionVisitor

_alphabet = set(string.printable)


class CharacterLattice(BottomMixin):

    def __repr__(self, maybe=set(), certainly=_alphabet):
        self._maybe = maybe
        self._certainly = certainly

    @property
    def maybe(self):
        return self._maybe
    @property
    def certainly(self):
        return self._certainly

    def top(self):
        return self._replace(CharacterLattice)

    def is_top(self) -> bool:
        return self.maybe == set() and self.certainly == _alphabet

    def _less_equal(self, other: 'CharacterLattice') -> bool:
        return self.certainly.issuperset(other.certainly) and self.maybe.issubset(other.maybe)

    def _join(self, other: 'CharacterLattice') -> 'CharacterLattice':
        maybe = self.maybe.intersection(other.maybe)
        certainly = self.certainly.intersection(other.certainly)
        return self._replace(CharacterLattice(maybe, certainly))

    def _meet(self, other: 'CharacterLattice'):
        maybe = self.maybe.union(other.maybe)
        certainly = self.certainly.intersection(other.certainly)
        return self._replace(CharacterLattice(maybe, certainly))

    def _widening(self, other: 'CharacterLattice'):
        return self._join(other)


class ConditionEvaluator(ExpressionVisitor):

    def visit_Literal(self, expr: 'Literal'):
        pass

    def visit_Input(self, expr: 'Input'):
        pass

    def visit_VariableIdentifier(self, expr: 'VariableIdentifier'):
        pass

    def visit_ListDisplay(self, expr: 'ListDisplay'):
        pass

    def visit_Range(self, expr: 'Range'):
        pass

    def visit_AttributeReference(self, expr: 'AttributeReference'):
        pass

    def visit_Subscription(self, expr: 'Subscription'):
        pass

    def visit_Slicing(self, expr: 'Slicing'):
        pass

    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation'):
        pass

    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation'):
        pass

    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation'):
        pass

    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation'):
        pass

    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation'):
        pass


class CharacterDomain(Store, InputMixin):

    def __init__(self, variables: Set[VariableIdentifier]):
        lattices = defaultdict(lambda: CharacterLattice)
        arguments = defaultdict(lambda : {'variables': variables})
        super().__init__(variables, lattices, arguments)
        self._variables = variables

    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'InputMixin':
        pass

    def unify(self, other: 'InputMixin') -> 'InputMixin':
        pass

    def _assign(self, left: Expression, right: Expression) -> 'State':
        raise Exception("Assignment should not be called in backward analysis.")

    def _assume(self, condition: Expression) -> 'State':
        pass

    def enter_if(self) -> 'State':
        return self

    def exit_if(self) -> 'State':
        return self

    def enter_loop(self) -> 'State':
        return self

    def exit_loop(self) -> 'State':
        return self

    def _output(self, output: Expression) -> 'State':
        return self

    def _substitute(self, left: Expression, right: Expression) -> 'State':
        pass
