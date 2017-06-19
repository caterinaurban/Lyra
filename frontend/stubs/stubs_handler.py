import ast
import frontend.stubs.stubs_paths as paths


class StubsHandler:
    asts = []

    def __init__(self, pre_analyzer):
        files = paths.all_files
        for file in files:
            r = open(file)
            tree = ast.parse(r.read())
            r.close()
            pre_analyzer.add_stub_ast(tree)
            self.asts.append(tree)

    @staticmethod
    def infer_file(tree, context, solver, used_names, infer_func):
        # Infer only structs that are used in the program to be inferred

        # Function definitions
        relevant_nodes = [node for node in tree.body
                          if (isinstance(node, ast.FunctionDef) and
                              node.name in used_names)]

        # Class definitions
        relevant_nodes += [node for node in tree.body
                           if (isinstance(node, ast.ClassDef) and
                               node.name in used_names)]

        for stmt in relevant_nodes:
            infer_func(stmt, context, solver)

    @classmethod
    def infer_all_files(cls, context, solver, used_names, infer_func):
        for tree in cls.asts:
            cls.infer_file(tree, context, solver, used_names, infer_func)
