cases: int = int(input())
for cc in range(10):
    distance: int = int(input())
    n: int = int(input())
    max_time: int = 0
    for i in range(20):
        position: int = int(input())
        speed: int = int(input())
        val: int = (distance - position) / speed
        if val > max_time:
            max_time: int = val
    print('Case #')
    print(cc+1)
    print(":")
    print(distance / max_time)
