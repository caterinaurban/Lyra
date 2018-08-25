
# INITIAL: a -> [-inf, inf]
a: bool = False
# STATE: a -> [0, 0]
if a:
    # STATE: a -> ⊥
    a = a
    # STATE: a -> ⊥
else:
    # STATE: a -> [0, 0]
    a = a
    # STATE: a -> [0, 0]
# FINAL: a -> [0, 0]
