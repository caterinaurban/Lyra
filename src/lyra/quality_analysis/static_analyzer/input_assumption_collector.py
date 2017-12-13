from copy import deepcopy

from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice
from lyra.core.cfg import ControlFlowGraph, Loop, Edge
from collections import deque

from lyra.core.statements import Call, Assignment, VariableAccess, LiteralEvaluation


class InputAssumptionCollector:

    def __init__(self, cfg: ControlFlowGraph, input_assumptions):
        self.cfg = cfg
        self.node_to_input = dict()
        self.nodes_done = []
        self.edges_todo = list(cfg.edges.keys())
        self.edges_done = []
        self.input_assumptions = input_assumptions

    def collect_input_assumptions(self):
        """
        Iterates through the control flow graph and gathers information about the order
        the inputs are read and combines it with the assumptions

        :param cfg: Controlflowgraph
        :param input_assumptions: Assumption of inputs
        :return: Assumptions about inputs in correct order
        """

        current_node = self.cfg.in_node
        while len(self.edges_todo) > 0 or self.cfg.out_node not in self.nodes_done:
            # check if there are edges with (x, current_node) that have to be handled first
            edges_with_target = [e for e in self.edges_todo if e[1] == current_node
                                 and self.cfg.edges[e].kind != Edge.Kind.LOOP_OUT]
            if len(edges_with_target) > 0:
                current_node = edges_with_target[0][0]
                continue

            # check if current_node already analyzed
            if current_node not in self.nodes_done:

                # if loop_in do special separate analysis
                if isinstance(current_node, Loop):
                    self.analyze_loop(current_node, current_node, dict())

                if not self.analyze_node(current_node, self.node_to_input):
                    break

            self.nodes_done.append(current_node)

            if current_node == self.cfg.out_node:
                break

            next_edge = [e for e in self.edges_todo if e[0] == current_node][0]
            current_node = next_edge[1]
            # move edge from to do to done
            self.edges_todo.remove(next_edge)
            self.edges_done.append(next_edge)
            # y of (x,y) is now current_node

        return self.node_to_input[current_node]

    def analyze_node(self, current_node, node_to_input):
        # if multiple edges in done with (x, current_node)
            # merge, check if still enough information
        sources = [e[0] for e in self.edges_done if e[1] == current_node]
        if len(sources) == 1:
            source = sources[0]
            if source in node_to_input:
                node_to_input[current_node] = deepcopy(node_to_input[source])
        elif len(sources) > 1:
            if not self.handle_multiple_sources(sources, current_node, node_to_input):
                return False

        # analyze statements
        for stmt in current_node.stmts:
            self.analyze_stmt_for_input(stmt, current_node, node_to_input)
        return True

    def handle_multiple_sources(self, sources, current_node, node_to_input):
        merge_successful = True
        merged_assmps = deepcopy(node_to_input[sources[0]])
        for assmp in [node_to_input[source] for source in sources[1:]]:
            if len(assmp) != len(merged_assmps):
                node_to_input[current_node] = []
                merged_assmps = self.find_common_assmp(sources, self.edges_done)
                merge_successful = False
            for assmp1, assmp2 in zip(merged_assmps, assmp):
                assmp1.join(assmp2)
        node_to_input[current_node] = merged_assmps
        return merge_successful

    def find_common_assmp(self, nodes, edges, node_to_input):
        node_sources = [[n] for n in nodes]
        edges_todo = deepcopy(edges)
        #nodes_done = deepcopy(nodes)
        while len(edges_todo) > 0:
            for edge in edges_todo:
                for node_source in node_sources:
                    if edge[1] in node_source:
                        node_source.append(edge[0])
                if all(edge[0] in ns for ns in node_sources):
                    return node_to_input[edge[0]]

    def analyze_stmt_for_input(self, stmt, curr_node, node_to_input):
        """"""
        stmts_to_check = deque([stmt])
        while len(stmts_to_check) > 0:
            curr_stmt = stmts_to_check.pop()
            if isinstance(curr_stmt, Call):
                if curr_stmt.name == 'input':
                    pp_line = curr_stmt.pp.line
                    assmp_pp = [k for k in self.input_assumptions if k.line == pp_line][0]
                    assumption = self.input_assumptions[assmp_pp]
                    if curr_node in node_to_input:
                        node_to_input[curr_node].append(assumption)
                    else:
                        node_to_input[curr_node] = [assumption]
                else:
                    stmts_to_check.extend(curr_stmt.arguments)
            elif isinstance(curr_stmt, Assignment):
                stmts_to_check.extend([curr_stmt.left, curr_stmt.right])
            elif isinstance(curr_stmt, (VariableAccess, LiteralEvaluation)):
                continue
            else:
                raise NotImplementedError(f"Analysis for {type(curr_stmt)} not yet implemented")

    def analyze_loop(self, current_node, loop_in_node, node_to_input):
        # check if there are edges with (x, current_node) that have to be handled first
        edges_with_target = [e for e in self.edges_todo if e[1] == current_node
                             and self.cfg.edges[e].kind != Edge.Kind.LOOP_OUT]
        if len(edges_with_target) > 0:
            current_node = edges_with_target[0][0]
            self.analyze_loop(current_node, loop_in_node, node_to_input)

        # check if current_node already analyzed
        if current_node not in self.nodes_done:
            self.analyze_node(current_node, node_to_input)

        self.nodes_done.append(current_node)

        next_edge = [e for e in self.edges_todo if e[0] == current_node][0]
        current_node = next_edge[1]

        self.edges_todo.remove(next_edge)
        self.edges_done.append(next_edge)

        if current_node == loop_in_node:
            # TODO put multiple of assumptions from local node_to_input into self.node_to_input
            return

        self.analyze_loop(current_node, loop_in_node, node_to_input)



    def analyze_loop_old(self, edges_todo, edges_done, current_node, loop_in_node, assumption, node_to_input, node_to_input_loop, iter_var, curr_iter, loop_cond, input_assumptions):
        """"""
        if current_node != loop_in_node:
            # check if there are edges with (x, current_node)
            edges_with_target = [e for e in edges_todo if e[1] == current_node]
            if len(edges_with_target) > 0:
                self.analyze_loop(edges_todo, edges_done, edges_with_target[0][0], loop_in_node, assumption, node_to_input, node_to_input_loop, iter_var, curr_iter, loop_cond, input_assumptions)


        # if multiple edges in done with (x, current_node)
            # merge, check if still enough information
        sources = [e[0] for e in edges_done if e[1] == current_node]
        if len(sources) == 1:
            source = sources[0]
            if source in node_to_input:
                node_to_input[current_node] = deepcopy(node_to_input[source])
        elif len(sources) > 1:
            self.handle_multiple_sources(self, node_to_input, sources, edges_done, current_node)

        # analyze statements
        for stmt in current_node.stmts:
            self.analyze_stmt_for_input(stmt, current_node, node_to_input, input_assumptions)


        next_edges = [e for e in edges_todo if e[0] == current_node]

        if len(next_edges) == 0:
            return
        next_edge = next_edges[0]
        current_node = next_edge[1]
        edges_todo.remove(next_edge)
        edges_done.append(next_edge)

        if current_node == loop_in_node:
            return

        self.analyze_loop(edges_todo, edges_done, current_node, loop_in_node, assumption, node_to_input, node_to_input_loop, iter_var, curr_iter, loop_cond, input_assumptions)