# INITIAL [3 x [2:(Any, [-inf, inf])] with delimiter '', 3:(Int, [-inf, 10]), 4 x [8:(Any, [-inf, inf])] with delimiter '', 9:(Int, [-inf, 20]), 11 x [14:(Any, [-inf, inf])] with delimiter '']
x: List[str] = input().split()
y: int = int(input())
if y > 10:
    raise ValueError
print(x[2])

x: List[str] = input().split()
y: int = int(input())
if y > 20:
    raise ValueError
print(x[3])

values: List[str] = input().split()
values2: List[str] = values
print(values2[10])