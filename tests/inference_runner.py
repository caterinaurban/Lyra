from frontend.stmt_inferrer import *
from frontend.context import Context
import frontend.z3_types as z3_types

r = open("tests/test.py")
t = ast.parse(r.read())
context = Context()
for stmt in t.body:
    infer(stmt, context)

z3_types.solver.push()

z3_types.solver.check()
model = z3_types.solver.model()


def print_types(pre, name, node):
    print(pre, end='')
    if isinstance(node, Class):
        print("{}: Class:".format(name))
        for t in node.types_map:
            print_types(pre + "   ", t, node.types_map[t])
    elif isinstance(node, Instance):
        print("{}: Instance({})".format(name, node.cls.name))
    else:
        print("{}: {}".format(name, model[node]))


for v in context.types_map:
    z3_t = context.types_map[v]
    print_types("", v, z3_t)




