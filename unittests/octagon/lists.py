x = int(input())
y = int(input())
z = int(input())

# ensure inputs are positive
if x < 0:
    x = -x
if y < 0:
    y = -y
if z < 0:
    z = -z

list1 = [x, y, z]
list1[1] = 1
