# INITIAL [2:(Int, [-inf, inf])]
a: int = int(input())
if a > 10:
    if a > 20:
        for i in range(30):
            values: List[str] = input().split(",")
    else:
        for i in range(20):
            values: List[str] = input().split(";")
else:
    if a > 20:
        for i in range(40):
            values: List[str] = input().split(",")
    else:
        for i in range(10):
            values: List[str] = input().split(",")
