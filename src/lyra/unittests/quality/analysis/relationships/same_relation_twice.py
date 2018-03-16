# INITIAL [2:(Int, [-inf, inf]), 3:((Int, [-inf, inf]), {.ID=3 - .ID=2 + 1 <= 0})]
a: int = int(input())
b: int = int(input())
if a <= b:
    raise ValueError
if b >= a:
    raise ValueError