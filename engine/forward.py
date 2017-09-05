from abstract_domains.state import State
from collections import deque
from copy import deepcopy
from core.cfg import Basic, Loop, Conditional, ControlFlowGraph, Edge
from engine.interpreter import Interpreter
from engine.result import AnalysisResult
from semantics.forward import ForwardSemantics
from queue import Queue


class ForwardInterpreter(Interpreter):
    def __init__(self, cfg: ControlFlowGraph, semantics: ForwardSemantics, widening: int):
        """Forward control flow graph interpreter.

        :param cfg: control flow graph to analyze 
        :param widening: number of iterations before widening 
        """
        super().__init__(cfg, semantics, widening)

    def analyze(self, initial: State) -> AnalysisResult:

        # prepare the worklist and iteration counts
        worklist = Queue()
        worklist.put(self.cfg.in_node)
        iterations = {node: 0 for node in self.cfg.nodes}

        while not worklist.empty():
            current = worklist.get()  # retrieve the current node

            iteration = iterations[current.identifier]

            # retrieve the previous entry state of the node
            if current in self.result.nodes:
                previous = deepcopy(self.result.get_node_result(current)[0])
            else:
                previous = None

            # compute the current entry state of the current node
            entry = deepcopy(initial)
            if current.identifier != self.cfg.in_node.identifier:
                entry.bottom()
                # join incoming states
                edges = self.cfg.in_edges(current)
                for edge in edges:
                    if edge.source in self.result.nodes:
                        predecessor = deepcopy(self.result.get_node_result(edge.source)[-1])
                    else:
                        predecessor = deepcopy(initial).bottom()
                    # handle conditional edges
                    if isinstance(edge, Conditional):
                        predecessor.next(edge.condition.pp, edge.kind)
                        predecessor = self.semantics.semantics(edge.condition, predecessor).filter()
                    # handle non-default edges
                    if edge.kind == Edge.Kind.IF_IN:
                        predecessor = predecessor.enter_if()
                    elif edge.kind == Edge.Kind.IF_OUT:
                        predecessor = predecessor.exit_if()
                    elif edge.kind == Edge.Kind.LOOP_IN:
                        predecessor = predecessor.enter_loop()
                    elif edge.kind == Edge.Kind.LOOP_OUT:
                        predecessor = predecessor.exit_loop()
                    entry = entry.join(predecessor)
                # widening
                if isinstance(current, Loop) and self.widening < iteration:
                    entry = deepcopy(previous).widening(entry)

            # check for termination and execute block
            if previous is None or not entry.less_equal(previous):
                states = deque([entry])
                if isinstance(current, Basic):
                    successor = entry
                    for stmt in current.stmts:
                        successor = deepcopy(successor)
                        successor.next(stmt.pp)
                        successor = self.semantics.semantics(stmt, successor)
                        states.append(successor)
                elif isinstance(current, Loop):
                    # nothing to be done
                    pass
                self.result.set_node_result(current, list(states))
                # update worklist and iteration count
                for node in self.cfg.successors(current):
                    worklist.put(node)
                iterations[current.identifier] = iteration + 1

        return self.result
