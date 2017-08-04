x = int(input())
y = int(input())
z = int(input())
list1 = [x, y, z]

q = 2  # q get used later indirectly via list1
list1[1] = list1[1] + 3  # this is not an overwrite
print(list1[1])  # now list1[1] is also used
list1[1] = list1[1] + list1[2]  # should not change anything to used since list1[1] and list1[2] currently unused
list1[q] = q  # this is an overwrite in list1 at index 2
r = list1[2] + list1[2]

print(r)
