
x: int = int(input())
y: int = int(input())
# list1 -> (O@0:4), s -> O; x -> U; y -> N
list1: List[int] = [1, x, 2, 3, 5, 8, y]
s: int = 0

s: int = s + list1[2]
s: int = s + list1[1]
s: int = s + list1[4]
s: int = s + list1[3]
s: int = s + list1[0]

print(s)
