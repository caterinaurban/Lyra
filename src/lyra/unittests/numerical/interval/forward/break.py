
for x in range(10):
    # STATE:  x -> [0, 9], y -> [-inf, inf]
    x = x # dummy assignment
    if x > 7:
        # STATE: x -> [8, 9], y -> [-inf, inf]
        x: int = x + 2
        # STATE: x -> [10, 11], y -> [-inf, inf]
    else:
        # STATE: x -> [0, 7], y -> [-inf, inf]
        x: int = x + 1
        # STATE: x -> [1, 8], y -> [-inf, inf]
        if x == 8:
            # STATE: x -> [8, 8], y -> [-inf, inf]
            x = x       # dummy assignment
            break
        # STATE: x -> [1, 7], y -> [-inf, inf]
        x = x  # dummy assignment
        # STATE: x -> [1, 7], y -> [-inf, inf]
    # STATE: x -> [1, 11], y -> [-inf, inf]
    for y in range(20):
        # STATE: x -> [1, 11], y -> [0, 19]
        if y > x:
            # STATE: x -> [1, 11], y -> [2, 19]
            break
        # STATE: x -> [1, 11], y -> [0, 11]
        if y > 10:
            # STATE: x -> [1, 11], y -> [11, 11]
            break
        # STATE: x -> [1, 11], y -> [0, 10]
    x = x   # dummy assignment
    # STATE: x -> [1, 11], y -> [-inf, inf]
