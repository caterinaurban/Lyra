
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
    for y in range(20):
        if y > x:
            break
        if y > 10:
            break
    x = x   # dummy assignment
    # STATE: x -> [1, 11], y -> [-inf, inf]
