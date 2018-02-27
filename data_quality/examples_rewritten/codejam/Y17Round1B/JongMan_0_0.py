# analysis finds cases x [int, int, n x [int, int]]

cases: int = int(input())
for cc in range(cases):
    distance: int = int(input())  # instead of distance, n = int(input())
    n: int = int(input())
    max_time: int = 0
    for i in range(n):
        position: int = int(input())  # instead of position, speed = int(input())
        speed: int = int(input())
        val: int = (distance - position) + speed  # instead of division
        if val > max_time:  # instead of max()
            max_time: int = val
    print('Case #')  # multiline output
    print(cc+1)
    print(":")
    print(distance / max_time)
