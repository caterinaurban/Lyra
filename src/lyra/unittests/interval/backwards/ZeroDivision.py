

a = input()
# RESULT: a -> [1,inf], b -> [-inf,inf], c -> [-inf,inf]
assert a > 0
# RESULT: a -> [-inf,inf], b -> [-inf,inf], c -> [-inf,inf]
b = 1 / a

a = input()
# RESULT: a -> [1,inf], b -> [-inf,inf], c -> [-inf,inf]
b = a
# RESULT: a -> [-inf,inf], b -> [1,inf], c -> [-inf,inf]
assert b > 0
# RESULT: a -> [-inf,inf], b -> [-inf,inf], c -> [-inf,inf]
c = 1 / b

a = input()
# RESULT: a -> [0,inf], b -> [-inf,inf], c -> [-inf,inf]
b = a + 1
# RESULT: a -> [-inf,inf], b -> [1,inf], c -> [-inf,inf]
assert b > 0
# RESULT: a -> [-inf,inf], b -> [-inf,inf], c -> [-inf,inf]
c = 1 / b

a = input()
# RESULT: a -> [5,inf], b -> [-inf,inf], c -> [-inf,inf]
a = a * 2
# RESULT: a -> [10,inf], b -> [-inf,inf], c -> [-inf,inf]
a = a - 9
# RESULT: a -> [1,inf], b -> [-inf,inf], c -> [-inf,inf]
assert a > 0
# RESULT: a -> [-inf,inf], b -> [-inf,inf], c -> [-inf,inf]
b = 1 / a

a = input()
# RESULT: a -> [6,inf], b -> [-inf,inf], c -> [-inf,inf]
b = a + 1 + 2 + (-8)
# RESULT: a -> [-inf,inf], b -> [1,inf], c -> [-inf,inf]
assert b > 0
# RESULT: a -> [-inf,inf], b -> [-inf,inf], c -> [-inf,inf]
c = 1 / b
# RESULT: a -> [-inf,inf], b -> [-inf,inf], c -> [-inf,inf]
