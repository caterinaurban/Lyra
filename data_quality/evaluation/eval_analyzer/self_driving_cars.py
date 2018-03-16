# Analysis finds:
# [1:(Int, [-inf, inf]),
# (.ID=1 + 0) x [3:(Float, [-inf, inf]),
    # 4:(Int, [-inf, inf]), (.ID=4 + 0) x [7:((Int, [-inf, inf]), [-.ID=3 + .ID=7 + 0 <= 0]),
    # 10:(Float, [0, inf])]]]

# Manually:
# [1:int, ID1 x [2:float, 3:int], ID3 x [4:int, 5:float]]
# ID5 > 0
# ID3 > 0
# ID2 >= ID4

# Differences:
# ID5 > 0 not only >= 0
# ID3 > 0


# input is int
cases: int = int(input())
for cc in range(cases):
    # input is float
    distance: float = float(input())
    # input is int
    n: int = int(input())
    max_time: float = 0
    # n > 0 because otherwise max_time = 0
    for i in range(n):
        # input is int
        position: int = int(input())
        # distance >= position
        if distance < position:
            raise ValueError("The distance cannot be smaller than the current position.")
        speed: float = float(input())
        # speed > 0
        if speed < 0:
            raise ValueError("The speed cannot be negative.")
        # speed != 0
        val: float = (distance - position) / speed
        if val > max_time:
            max_time: int = val
    print('Trip #')
    print(cc+1)
    print("with speed")
    # max_time != 0
    print(distance / max_time)
    print("")
