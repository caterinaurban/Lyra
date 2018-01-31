# INITIAL [2:(Int, [-inf, inf]), 4:((Float, [-inf, inf]), [-.ID=2 + .ID=4 + 1 <= 0])]
x: str = input()
x_float: float = float(x)
y: str = input()
x_int: int = int(x_float)
y_float: float = float(y)
if x_float <= y_float:
    raise ValueError
