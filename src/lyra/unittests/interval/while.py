
# INITIAL: x -> [-inf, inf]
x: int = 0
# STATE: x -> [0, 0]
while x < 9:    # LOOP: x -> [0, inf]
    # STATE: x -> [0, 8]
    x: int = x + 1
    # STATE: x -> [1, 9]
# FINAL: x -> [9, inf]
