x = int(input())
y = int(input())
z = int(input())

a = int(input())
b = int(input())

list1 = [x, y, z]

r = 0

# interesting switch: do we know relation of a and b or not?
b = a + 1
if x > 0:
    q = list1[a]
    list1[2] = 3
else:
    q = list1[b]

r = list1[2]
print(r + q)
