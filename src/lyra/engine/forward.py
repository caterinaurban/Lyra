"""
Forward Analysis Engine
=======================

:Author: Caterina Urban
"""

from collections import deque
from copy import deepcopy
from queue import Queue

from lyra.engine.interpreter import Interpreter
from lyra.engine.result import AnalysisResult
from lyra.semantics.forward import ForwardSemantics

from lyra.abstract_domains.state import State
from lyra.core.cfg import Basic, Loop, Conditional, ControlFlowGraph, Edge


class ForwardInterpreter(Interpreter):
    """Forward control flow graph interpreter."""
    def __init__(self, cfg: ControlFlowGraph, semantics: ForwardSemantics, widening, initial):
        """Forward control flow graph interpreter construction.

        :param cfg: control flow graph to analyze
        :param semantics: semantics of statements in the control flow graph
        :param widening: number of iterations before widening
        :param initial: initial analysis state
        """
        super().__init__(cfg, semantics, widening, initial)

    def analyze(self) -> AnalysisResult:

        # prepare the worklist and iteration counts
        worklist = Queue()
        worklist.put(self.cfg.in_node)
        iterations = {node: 0 for node in self.cfg.nodes}

        while not worklist.empty():
            current = worklist.get()  # retrieve the current node

            iteration = iterations[current.identifier]

            # retrieve the previous entry state of the node
            if current in self.result.result:
                previous = deepcopy(self.result.get_node_result(current)[0])
            else:
                previous = None

            # compute the current entry state of the current node
            entry = deepcopy(self.initial)
            if current.identifier != self.cfg.in_node.identifier:
                entry.bottom()
                # join incoming states
                edges = self.cfg.in_edges(current)
                for edge in edges:
                    if edge.source in self.result.result:
                        predecessor = deepcopy(self.result.get_node_result(edge.source)[-1])
                    else:
                        predecessor = deepcopy(self.initial).bottom()
                    # handle conditional edges
                    if isinstance(edge, Conditional) and edge.kind == Edge.Kind.DEFAULT:
                        neighbors = self.cfg.out_edges(edge.source)
                        branch = any(edge.kind == Edge.Kind.IF_IN for edge in neighbors)
                        loop = any(edge.kind == Edge.Kind.LOOP_IN for edge in neighbors)
                        assert (branch or loop) and not (branch and loop)
                        predecessor = predecessor.enter_if() if branch else predecessor
                        predecessor = predecessor.enter_loop() if loop else predecessor
                        condition = edge.condition
                        predecessor = predecessor.before(condition.pp)
                        predecessor = self.semantics.semantics(condition, predecessor).filter()
                        predecessor = predecessor.exit_if() if branch else predecessor
                        predecessor = predecessor.exit_loop() if loop else predecessor
                    elif edge.kind == Edge.Kind.IF_IN:
                        predecessor = predecessor.enter_if()
                        assert isinstance(edge, Conditional)
                        condition = edge.condition
                        predecessor = predecessor.before(condition.pp)
                        predecessor = self.semantics.semantics(condition, predecessor).filter()
                    elif edge.kind == Edge.Kind.LOOP_IN:
                        predecessor = predecessor.enter_loop()
                        assert isinstance(edge, Conditional)
                        condition = edge.condition
                        predecessor = predecessor.before(condition.pp)
                        predecessor = self.semantics.semantics(condition, predecessor).filter()
                    # handle unconditional non-default edges
                    if edge.kind == Edge.Kind.IF_OUT:
                        predecessor = predecessor.exit_if()
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
                        successor = successor.before(stmt.pp)
                        successor = self.semantics.semantics(stmt, deepcopy(successor))
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
