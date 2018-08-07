from collections import defaultdict
from copy import deepcopy
from typing import Set, List, Dict

from lyra.abstract_domains.assumption.assumption_domain import JSONMixin, InputMixin
from lyra.abstract_domains.string.character_domain import CharacterLattice, CharacterState
from lyra.assumption.error import CheckerError, DependencyError
from lyra.core.expressions import VariableIdentifier, Expression


class AlphabetLattice(CharacterLattice, JSONMixin):

    def to_json(self) -> dict:
        js = {
            'certainly': list(self.certainly),
            'maybe': list(self.maybe)
        }
        return js

    @staticmethod
    def from_json(json: dict) -> 'JSONMixin':
        return AlphabetLattice(set(json['certainly']), set(json['maybe']))

    def check_input(self,  pp: VariableIdentifier, pp_value: dict, line_errors: Dict[int, List[CheckerError]]):
        if self.is_top():
            return
        input_line = pp_value[pp][0]
        input_value = pp_value[pp][1]
        if input_value is not None:
            input_value = set(input_value)
            error_message = ""
            if not input_value.issuperset(self.certainly):
                s = ', '.join(['\'' + c + '\'' for c in self.certainly])
                error_message += "This value must contain *all* the characters: {}".format(s)

            if not input_value.issubset(self.maybe):
                if len(error_message) > 0:
                    error_message += "; \n"
                s = ', '.join(['\'' + c + '\'' for c in self.maybe])
                error_message += "This value must contain *only* the characters: {}".format(s)
            if len(error_message) > 0:
                error = CheckerError(error_message)
                line_errors[input_line].append(error)
        else:
            error = DependencyError(input_line)
            line_errors[input_line].append(error)


class AlphabetState(CharacterState, InputMixin):

    def __init__(self, variables: Set[VariableIdentifier], precursory: InputMixin = None):
        lattices = defaultdict(lambda: AlphabetLattice)
        super(CharacterState, self).__init__(variables, lattices)
        InputMixin.__init__(self, precursory)

    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'InputMixin':
        return self

    def unify(self, other: 'InputMixin') -> 'InputMixin':
        return self

    class Refinement(CharacterState.ExpressionRefinement):

        def visit_Input(self, expr: 'Input', state=None, evaluation=None, value=None):
            state.record(deepcopy(value))
            return state
    _refinement = Refinement()
