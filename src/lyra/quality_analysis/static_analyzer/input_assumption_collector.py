from copy import deepcopy

from lyra.core.cfg import ControlFlowGraph, Loop, Edge
from collections import deque

from lyra.core.statements import Call, Assignment, VariableAccess, LiteralEvaluation
from lyra.core.types import IntegerLyraType


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
                if isinstance(current_node, Loop):
                    input_assmps = self.analyze_loop(current_node)
                    information_loss = not self.get_prev_assmp(current_node, self.node_to_input)
                    if information_loss:
                        break
                    self.node_to_input[current_node].extend(input_assmps)
                else:
                    information_loss = not self.analyze_node(current_node, self.node_to_input)
                    if information_loss:
                        break

            self.nodes_done.append(current_node)

            if current_node == self.cfg.out_node:
                break

            next_edge = [e for e in self.edges_todo if e[0] == current_node][0]
            current_node = next_edge[1]

            self.edges_todo.remove(next_edge)
            self.edges_done.append(next_edge)

        return self.node_to_input[current_node]

    def get_prev_assmp(self, current_node, node_to_input):
        sources = [e[0] for e in self.edges_done if e[1] == current_node
                   and self.cfg.edges[e].kind != Edge.Kind.LOOP_OUT]
        if len(sources) == 1:
            if sources[0] in node_to_input:
                node_to_input[current_node] = deepcopy(node_to_input[sources[0]])
        elif len(sources) > 1:
            if not self.handle_multiple_sources(sources, current_node, node_to_input):
                return False
        return True

    def analyze_node(self, current_node, node_to_input):
        if len(node_to_input.keys()) > 0:
            if not self.get_prev_assmp(current_node, node_to_input):
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
                merged_assmps = self.find_common_assmp(sources, self.edges_done, node_to_input)
                merge_successful = False
            for assmp1, assmp2 in zip(merged_assmps, assmp):
                assmp1.join(assmp2)
        node_to_input[current_node] = merged_assmps
        return merge_successful

    def find_common_assmp(self, nodes, edges, node_to_input):
        node_sources = [[n] for n in nodes]
        edges_todo = deepcopy(edges)
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

    def analyze_loop(self, current_node):
        loop_node_to_input = dict()
        loop_in_node = current_node
        one_iter_done = False
        while current_node != loop_in_node or not one_iter_done:
            one_iter_done = True
            # check if there are edges with (x, current_node) that have to be handled first
            edges_with_target = [e for e in self.edges_todo if e[1] == current_node
                                 and self.cfg.edges[e].kind != Edge.Kind.LOOP_OUT]
            if len(edges_with_target) > 0:
                current_node = edges_with_target[0][0]
                self.analyze_loop(current_node)

            # check if current_node already analyzed
            if current_node not in self.nodes_done:
                self.analyze_node(current_node, loop_node_to_input)

            self.nodes_done.append(current_node)

            next_edges = [e for e in self.edges_todo if e[0] == current_node]
            if current_node == loop_in_node:
                next_edge = [e for e in next_edges if self.cfg.edges[e].kind == Edge.Kind.LOOP_IN][0]
            else:
                next_edge = next_edges[0]
            current_node = next_edge[1]

            self.edges_todo.remove(next_edge)
            self.edges_done.append(next_edge)

        condition_edge = [e for e in self.edges_done if e[0] == current_node
                                     and self.cfg.edges[e].kind == Edge.Kind.LOOP_IN][0]
        condition = self.cfg.edges[condition_edge].condition
        num_iter = self.find_number_of_iterations(condition)
        return loop_node_to_input[next_edge[0]] * num_iter

    def find_number_of_iterations(self, condition):
        if not (isinstance(condition, Call) and condition.name == 'in'):
            raise NotImplementedError("Loop analysis only implemented for \'in\' condition.")
        in_argument = condition.arguments[1]
        if isinstance(in_argument, Call) and in_argument.name == 'range':
            if len(in_argument.arguments) == 1:
                num_range = in_argument.arguments[0]
                if isinstance(num_range, LiteralEvaluation):
                    num_range_literal = num_range.literal
                    if isinstance(num_range_literal.typ, IntegerLyraType):
                        return int(num_range_literal.val)
                    else:
                        error = f"Loop analysis not implemented for range call with argument type {num_range_literal.typ}."
                        raise NotImplementedError(error)
                else:
                    error = f"Loop analysis not implemented for range call with argument {num_range}."
                    raise NotImplementedError(error)
            else:
                error = f"Loop analysis not implemented for range call with {len(in_argument.arguments)} arguments"
                raise NotImplementedError(error)
        else:
            error = f"Loop analysis not implemented for condition {condition}"
            raise NotImplementedError(error)
