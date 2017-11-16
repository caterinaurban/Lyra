
a = input()
# RESULT: a -> [-49,inf], b -> [-inf,inf]
b = 50 + a
assert b > 0

a = input()
# RESULT: a -> [-inf,49], b -> [-inf,inf]
b = 50 - a
assert b > 0

a = input()
# RESULT: a -> [51,inf], b -> [-inf,inf]
b = a - 50
assert b > 0

a = input()
# RESULT: a -> [10,inf], b -> [-inf,inf]
b = 50 * a
assert b > 500

a = input()
# RESULT: a -> [0,9], b -> [-inf,inf]
b = 500 / a
assert b > 50

a = input()
# RESULT: a -> [25050,inf], b -> [-inf,inf]
b = a / 50
assert b > 500

a = input()
# RESULT: a -> [-inf,49], b -> [-inf,inf]
b = 50 + (-a)
assert b > 0

a = input()
# RESULT: a -> [-inf,49], b -> [-inf,inf]
b = 60 - 20 + (-a) + 10
assert b > 0
