import time

from lyra.abstract_domains.quality.assumption_domain import AssumptionState
from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, \
    MultiInputAssumptionLattice
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics


class AssumptionAnalysis(Runner):

    def __init__(self, do_render=True):
        super().__init__()
        self.do_render = do_render

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return AssumptionState(self.variables)

    def run(self):
        start = time.time()
        result = self.interpreter().analyze(self.state())
        analysis = round((time.time()-start)*100000)
        sub_time1 = 0
        assume_time = 0
        pop_case = 0
        pop_loop = 0
        for states in result.result.values():
            for state in states:
                sub_time1 += state.substitute_time
                assume_time += state.assume_time
                pop_case += state.pop_case
                pop_loop += state.pop_loop
        print(f"substitute_time:{sub_time1}")
        print(f"assume_time:{assume_time}")
        print(f"pop_case:{pop_case}")
        print(f"pop_loop:{pop_loop}")
        print(f"-----analysis:{analysis}")
        show_simple = True
        if show_simple:
            for node, items in result.result.items():
                if node.identifier == 1:
                    items[0] = self.result_to_input_assmps(items[0].stack_top.assmps)
        if self.do_render:
            self.render(result)
        return result

    def result_to_input_assmps(self, assmps):
        new_assmps = []
        for assmp in assmps:
            #if isinstance(assmp, AssumptionLattice):
            if isinstance(assmp, MultiInputAssumptionLattice):
                inner_assmps = self.result_to_input_assmps(assmp.assmps)
                assmp.assmps = inner_assmps
                new_assmps.append(assmp)
            else:
                relations = assmp.relations.store[assmp.var_name]
                new_assmps.append((assmp.assmp.type_assumption, relations))
            #else:
            #    assmp._assmps = self.result_to_input_assmps(assmp.assmps)
            #    new_assmps.append(assmp)
        return new_assmps
