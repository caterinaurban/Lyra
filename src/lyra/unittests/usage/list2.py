
b: bool = bool(input())
x: int = int(input())
y: int = int(input())
# RESULT: b -> U; list1 -> (O@0:4); list2 -> (O@0:2); s -> O; x -> U; y -> N
list1: List[int] = [1, x, 2, 3, 5, 8, y]
s: int = 0
if b:
    # some random accesses to list
    list2: List[int] = list1
    s: int = s + list2[2]
    s: int = s + list2[1]
else:
    # some different random accesses to list
    s: int = s + list1[4]
    s: int = s + list1[3]
    s: int = s + list1[0]
print(s)
