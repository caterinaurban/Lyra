
for x in range(10):
    # STATE:  x -> [0, 9]
    if x > 7:
        # STATE: x -> [8, 9]
        x: int = x + 2
        # STATE: x -> [10, 11]
    else:
        # STATE: x -> [0, 7]
        x: int = x + 1
        # STATE: x -> [1, 8]
        if x == 8:
            # STATE: x -> [8, 8]
            break
        # STATE: x -> [1, 7]
    # STATE: x -> [1, 11]
