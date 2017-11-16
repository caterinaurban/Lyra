

a = input()
# RESULT: a -> [-inf,-1], b -> [-inf,inf]
b = -a
assert b > 0

a = input()
# RESULT: a -> [-inf,0], b -> [-inf,inf]
b = -a + 1
assert b > 0

a = input()
# RESULT: a -> [-inf,-2], b -> [-inf,inf]
b = -(a + 1)
assert b > 0

a = input()
# RESULT: a -> [-inf,inf], b -> [-inf,inf]
b = -1
assert b > 0

a = input()
# RESULT: a -> [-inf,0], b -> [-inf,inf]
b = 1 + (-a)
assert b > 0

a = input()
# RESULT: a -> [-inf,-2], b -> [-inf,inf]
b = -(1 + a)
assert b > 0

a = input()
# RESULT: a -> [2,inf], b -> [-inf,inf]
b = -(1 + -a)
assert b > 0
