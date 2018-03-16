# INITIAL [2:(Int, [-inf, inf]), 3:((Int, [-inf, inf]), {-.ID=2 + .ID=3 + 1 <= 0})]
x: int = int(input())
y: int = int(input())
if x <= y:
    raise ValueError
