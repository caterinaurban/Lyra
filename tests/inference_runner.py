from frontend.stmt_inferrer import *

r = open("tests/expressions_test.py")
t = ast.parse(r.read())
context = Context()
for stmt in t.body:
    infer(stmt, context, None)

for key in sorted(context.types_map):
    print("{} : {}".format(key, context.types_map[key]))
