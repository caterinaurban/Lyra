
# INITIAL: i -> [-inf, inf], b -> [-inf, inf]
i: int = 0
for i in range(10):
    # STATE: i -> [0, 10], b -> [-inf, inf]
    b: int = 1
    # STATE: a -> [0, 10], b -> [1, 1]
# FINAL: a -> [11, inf], b -> [1, 2]
