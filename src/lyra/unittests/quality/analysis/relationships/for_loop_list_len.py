# INITIAL [2:(Int, [-inf, inf]), (.ID=2 + 0) x [2 x [4:(Any, [-inf, inf])] with delimiter ',']]
N: int = int(input())
for i in range(N):
    fields: List[str] = input().split(",")
    f_zero: int = fields[0]
    f_one: str = fields[1]
    z: int = int(f_one)
    y: int = int(fields[-1])

