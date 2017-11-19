x: int = int(input())
y: int = int(input())

list1: List[int] = [x, 2, 3, 5, 8, y]

sum: int = 0

i: int = 0
l: int = len(list1)
l: int = l - 1

while i <= l:
    i: int = i + 1
    sum: int = sum + list1[i]  # bug: list1[0] is not summed up

print(sum)
