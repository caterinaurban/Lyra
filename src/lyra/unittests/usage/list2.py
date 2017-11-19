b: bool = bool(input())
x: int = int(input())
y: int = int(input())
# RESULT: b -> U, list1 -> (O@0:4), list2 -> (O@0:2), sum -> O, x -> U, y -> N
list1: List[int] = [1, x, 2, 3, 5, 8, y]
sum: int = 0
if b:
    # some random accesses to list
    list2: List[int] = list1
    sum: int = sum + list2[2]
    sum: int = sum + list2[1]
else:
    # some different random accesses to list
    sum: int = sum + list1[4]
    sum: int = sum + list1[3]
    sum: int = sum + list1[0]
print(sum)
