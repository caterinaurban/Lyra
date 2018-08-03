
# INITIAL: 3:(Integer, ⊤), 3.1 * [5:(Float, ≥0), 8:(Integer, ⊤), 8.1 * [11:(Integer, ⊤), 14:(Float, >0)]]
cases: int = int(input())
for case in range(cases):
    distance: float = float(input())
    if distance < 0:
        raise ValueError("Distance cannot be negative.")
    n: int = int(input())
    max: float = 0
    for i in range(n):
        position: int = int(input())
        if distance < position:
            raise ValueError("Distance cannot be smaller than the current position.")
        speed: float = float(input())
        if speed < 0:
            raise ValueError("Speed cannot be negative.")
        val: float = (distance - position) / speed
        if val > max:
            max: int = val
    print("Trip:")
    print(case + 1)
    print("with speed")
    print(distance / max)
# FINAL: ε
