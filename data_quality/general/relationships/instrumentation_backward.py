"""
Backward Analysis Engine
========================

:Author: Caterina Urban
"""

from collections import deque
from copy import deepcopy
from queue import Queue

import time

from lyra.engine.interpreter import Interpreter
from lyra.engine.result import AnalysisResult
from lyra.semantics.backward import BackwardSemantics

from lyra.abstract_domains.state import State
from lyra.core.cfg import Basic, Loop, Conditional, ControlFlowGraph, Edge


class BackwardInterpreter(Interpreter):
    """Backward control flow graph interpreter."""
    def __init__(self, cfg: ControlFlowGraph, semantics: BackwardSemantics, widening: int):
        """Backward control flow graph interpreter construction.

        :param cfg: control flow graph to analyze
        :param widening: number of iterations before widening 
        """
        super().__init__(cfg, semantics, widening)

    @property
    def semantics(self):
        return self._semantics

    def analyze(self, initial: State) -> AnalysisResult:

        # prepare the worklist and iteration counts
        worklist = Queue()
        worklist.put(self.cfg.out_node)
        iterations = {node: 0 for node in self.cfg.nodes}

        time1 = 0
        time2 = 0
        time3 = 0
        time4 = 0
        time5 = 0
        time6 = 0
        time7 = 0
        time8 = 0
        time9 = 0
        time10 = 0

        while not worklist.empty():
            start = time.time()
            current = worklist.get()  # retrieve the current node

            iteration = iterations[current.identifier]

            # retrieve the previous exit state of the node
            if current in self.result.result:
                previous = deepcopy(self.result.get_node_result(current)[-1])
            else:
                previous = None

            # compute the current exit state of the current node
            entry = deepcopy(initial)
            time1 += round((time.time()-start)*100000)
            if current.identifier != self.cfg.out_node.identifier:
                start = time.time()
                entry.bottom()
                # join incoming states
                edges = self.cfg.out_edges(current)
                time2 += round((time.time()-start)*100000)
                start = time.time()
                for edge in edges:
                    if edge.target in self.result.result:
                        start_inner = time.time()
                        successor = deepcopy(self.result.get_node_result(edge.target)[0])
                        time9 += round((time.time()-start_inner)*100000)

                    else:
                        start_inner = time.time()
                        successor = deepcopy(initial).bottom()
                        time10 += round((time.time()-start_inner)*100000)
                    # handle unconditional non-default edges
                    if edge.kind == Edge.Kind.IF_OUT:
                        successor = successor.enter_if()
                    elif edge.kind == Edge.Kind.LOOP_OUT:
                        successor = successor.enter_loop()
                    # handle conditional edges
                    if isinstance(edge, Conditional) and edge.kind == Edge.Kind.DEFAULT:
                        start_inner = time.time()
                        branch = any(edge.kind == Edge.Kind.IF_IN for edge in edges)
                        loop = any(edge.kind == Edge.Kind.LOOP_IN for edge in edges)
                        assert (branch or loop) and not (branch and loop)
                        successor = successor.enter_if() if branch else successor
                        successor = successor.enter_loop() if loop else successor
                        successor = successor.before(edge.condition.pp)
                        successor = self.semantics.semantics(edge.condition, successor).filter()
                        successor = successor.exit_if() if branch else successor
                        successor = successor.exit_loop() if loop else successor
                        time6 += round((time.time()-start_inner)*100000)
                    if isinstance(edge, Conditional) and edge.kind == Edge.Kind.DEFAULT:
                        start_inner = time.time()
                        assert isinstance(edge, Conditional)
                        successor = successor.before(edge.condition.pp)
                        successor = self.semantics.semantics(edge.condition, successor).filter()
                        successor = successor.exit_if()
                        time7 += round((time.time()-start_inner)*100000)
                    elif edge.kind == Edge.Kind.LOOP_IN:
                        start_inner = time.time()
                        assert isinstance(edge, Conditional)
                        successor = successor.before(edge.condition.pp)
                        successor = self.semantics.semantics(edge.condition, successor).filter()
                        successor = successor.exit_loop()
                        time8 += round((time.time()-start_inner)*100000)
                    entry = entry.join(successor)
                time3 += round((time.time()-start)*100000)
                start = time.time()
                # widening
                if isinstance(current, Loop) and self.widening < iteration:
                    entry = deepcopy(previous).widening(entry)
                time4 += round((time.time()-start)*100000)
            start = time.time()
            # check for termination and execute block
            if previous is None or not entry.less_equal(previous):
                states = deque([entry])
                if isinstance(current, Basic):
                    successor = entry
                    for stmt in reversed(current.stmts):
                        successor = successor.before(stmt.pp)
                        successor = self.semantics.semantics(stmt, deepcopy(successor))
                        states.appendleft(successor)
                elif isinstance(current, Loop):
                    # nothing to be done
                    pass
                self.result.set_node_result(current, list(states))
                # update worklist and iteration count
                for node in self.cfg.predecessors(current):
                    worklist.put(node)
                iterations[current.identifier] = iteration + 1
            time5 += round((time.time()-start)*100000)

        print(f"time1: {time1}")
        print(f"time2: {time2}")
        print(f"time3: {time3}")
        print(f"time4: {time4}")
        print(f"time5: {time5}")

        print(f"time6: {time6}")
        print(f"time7: {time7}")
        print(f"time8: {time8}")

        print(f"time9: {time9}")
        print(f"time10: {time10}")

        return self.result
