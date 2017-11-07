from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.abstract_domains.state import State
from lyra.core.statements import Call


class UsageSemantics(DefaultBackwardSemantics):
    def user_defined_call_semantics(self, stmt: Call, state: State) -> State:
        raise NotImplementedError("Usage semantics for call statement {} not yet implemented!".format(stmt))
