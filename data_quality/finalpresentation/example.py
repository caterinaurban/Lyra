from typing import List

data: List[str] = input().split(",")
x: int = int(input())
print(data[x])
if x < 2:
    print(data[3])
else:
    print(data[4])
