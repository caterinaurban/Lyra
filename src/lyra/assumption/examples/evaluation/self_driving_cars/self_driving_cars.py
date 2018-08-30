# 2:(Integer, T, T), 2.1 * [4:(Float, OCT( +4.1 + 0.0 >= 0), T), 7:(Integer, T, T), 7.1 * [10:(
# Integer, OCT( -10.1 + 4.1 + 0.0 >= 0), T), 13:(Float, OCT( +13.1 + 0.0 >= 0), T)]] import sys
# sys.stdin = open('self_driving_cars.in', 'r')
cases: int = int(input())
for cc in range(cases):
    distance: float = float(input())
    if distance < 0:
        raise ValueError("Distance cannot be negative.")
    n: int = int(input())
    max_time: float = 0
    for i in range(n):
        position: int = int(input())
        if distance < position:
            raise ValueError("The distance cannot be smaller than the current position.")
        speed: float = float(input())
        if speed < 0:
            raise ValueError("The speed cannot be negative.")
        val: float = (distance - position) / speed
        if val > max_time:
            max_time: int = val
    t: int = cc + 1
    print('Trip #')
    print(t)
    print("with speed")
    print(distance)
    print("")
